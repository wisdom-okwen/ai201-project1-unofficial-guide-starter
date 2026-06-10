"""Semantic chunking (planning.md > Chunking Strategy).

Instead of splitting on a fixed character count, we split where the *meaning*
shifts:

  1. Break the document body into sentence-like units. Structural lines
     (=== headers ===) and list items (numbered / bulleted / [tagged]) are kept
     whole so an atomic fact -- one dorm, one study spot -- stays intact. Prose
     is split into sentences.
  2. Embed every unit with the same model used for retrieval and measure the
     cosine distance between each adjacent pair.
  3. Cut a chunk boundary wherever that distance exceeds the 90th percentile of
     distances within the document (a visible topic change).
  4. Apply guardrails: force-split any chunk over MAX_CHUNK_WORDS (the embedding
     model truncates past ~256 tokens) and merge any chunk under MIN_CHUNK_WORDS
     into a neighbour.
  5. Prepend the document's short source/topic header to each chunk for context
     and citation.
"""
from __future__ import annotations

import math
import re

import numpy as np

from config import BREAKPOINT_PERCENTILE, MAX_CHUNK_WORDS, MIN_CHUNK_WORDS
from ingest import Document

_STRUCTURAL = re.compile(r"^(===|---|#|\d+\.|[-*•]|\[)")
_SECTION_HEADER = re.compile(r"^(===|---|#)")   # a section title, e.g. "=== 3. Bicycling ==="
# split prose on sentence enders followed by whitespace + a capital/quote/digit
_SENTENCE = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'])')


def split_units(body: str) -> list[str]:
    """Break a body into sentence-like units, keeping structure intact."""
    units: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        if _STRUCTURAL.match(line):           # header or list item -> one unit
            units.append(line)
        else:                                 # prose -> one unit per sentence
            units.extend(p.strip() for p in _SENTENCE.split(line) if p.strip())
    return units


def _words(text: str) -> int:
    return len(text.split())


def _split_oversized(chunk: str, max_words: int) -> list[str]:
    """Split a too-long chunk into exactly `pieces` roughly equal parts.

    Each line is assigned to a bucket by its cumulative word position, which
    keeps the parts balanced and -- unlike greedy fill-to-target -- never spills
    a tiny sub-minimum tail into an extra piece.
    """
    total = _words(chunk)
    if total <= max_words:
        return [chunk]
    pieces = math.ceil(total / max_words)
    target = total / pieces
    buckets: list[list[str]] = [[] for _ in range(pieces)]
    cumulative = 0
    for line in chunk.split("\n"):
        idx = min(pieces - 1, int(cumulative / target))
        buckets[idx].append(line)
        cumulative += _words(line)
    return ["\n".join(b) for b in buckets if b]


def _merge_undersized(chunks: list[str], min_words: int) -> list[str]:
    """Merge chunks below min_words into an adjacent chunk."""
    merged: list[str] = []
    for chunk in chunks:
        if merged and _words(merged[-1]) < min_words:
            merged[-1] = merged[-1] + "\n" + chunk
        else:
            merged.append(chunk)
    # a tiny trailing chunk has no "next" to absorb it -> merge backwards
    if len(merged) >= 2 and _words(merged[-1]) < min_words:
        tail = merged.pop()
        merged[-1] = merged[-1] + "\n" + tail
    return merged


def _boundaries(units: list[str], embeddings: np.ndarray, percentile: float) -> list[int]:
    """Indices where a new chunk should start (cosine distance > percentile)."""
    # embeddings are L2-normalised, so cosine similarity == dot product
    sims = np.sum(embeddings[:-1] * embeddings[1:], axis=1)
    distances = 1.0 - sims
    threshold = np.percentile(distances, percentile)
    return [i + 1 for i, d in enumerate(distances) if d > threshold]


def chunk_document(doc: Document, model) -> list[str]:
    """Return the list of final chunk texts (header prepended) for one document."""
    units = split_units(doc.body)
    if not units:
        return []
    if len(units) == 1:
        return [f"{doc.header_prefix}\n{units[0]}"]

    embeddings = model.encode(units, normalize_embeddings=True)
    starts = set(_boundaries(units, embeddings, BREAKPOINT_PERCENTILE))

    groups: list[list[str]] = []
    current: list[str] = [units[0]]
    for i in range(1, len(units)):
        # start a new chunk at a semantic boundary, or whenever a section header
        # appears (so a "=== ... ===" title always leads its own section rather
        # than being stranded at the end of the previous chunk)
        if i in starts or _SECTION_HEADER.match(units[i]):
            groups.append(current)
            current = [units[i]]
        else:
            current.append(units[i])
    groups.append(current)

    raw_chunks = ["\n".join(g) for g in groups]

    # Merge tiny chunks first, then split oversized ones last, so MAX_CHUNK_WORDS
    # is a hard guarantee (merging can't push a chunk back over the cap).
    merged = _merge_undersized(raw_chunks, MIN_CHUNK_WORDS)
    sized: list[str] = []
    for chunk in merged:
        sized.extend(_split_oversized(chunk, MAX_CHUNK_WORDS))

    return [f"{doc.header_prefix}\n{chunk}" for chunk in sized]


def chunk_all(documents: list[Document], model) -> list[dict]:
    """Chunk every document; return chunk records with metadata for the vector store."""
    records: list[dict] = []
    for doc in documents:
        for idx, text in enumerate(chunk_document(doc, model)):
            records.append(
                {
                    "id": f"{doc.filename}::{idx}",
                    "text": text,
                    "metadata": {
                        "filename": doc.filename,
                        "source": doc.metadata.get("source", ""),
                        "url": doc.metadata.get("url", ""),
                        "topic": doc.metadata.get("topic", ""),
                        "chunk_index": idx,
                    },
                }
            )
    return records
