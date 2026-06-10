"""Milestone 3 driver: load -> clean -> semantic-chunk, then inspect.

Run:  .venv/bin/python build_chunks.py

Prints corpus/chunk statistics and 5 random chunks so you can eyeball whether
each chunk is readable, substantive, and self-contained before embedding.
Also writes chunks.json so later milestones (and you) can reuse the chunks
without recomputing them.
"""
from __future__ import annotations

import json
import random
import statistics

from sentence_transformers import SentenceTransformer

from chunking import chunk_all
from config import CHUNKS_PREVIEW, EMBEDDING_MODEL
from ingest import load_documents

SEED = 7  # fixed so "random" samples are reproducible across runs


def main() -> None:
    print(f"Loading embedding model: {EMBEDDING_MODEL} ...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    documents = load_documents()
    print(f"Loaded {len(documents)} documents\n")

    records = chunk_all(documents, model)
    word_counts = [len(r["text"].split()) for r in records]

    # --- statistics ---
    print("=" * 70)
    print("CHUNK STATISTICS")
    print("=" * 70)
    print(f"Total documents : {len(documents)}")
    print(f"Total chunks    : {len(records)}")
    print(f"Words per chunk : min {min(word_counts)} | "
          f"median {int(statistics.median(word_counts))} | "
          f"mean {statistics.mean(word_counts):.1f} | max {max(word_counts)}")
    print(f"Healthy range   : 50-2000 total chunks (per Milestone 3 checkpoint)\n")

    print("Chunks per document:")
    per_doc: dict[str, int] = {}
    for r in records:
        per_doc[r["metadata"]["filename"]] = per_doc.get(r["metadata"]["filename"], 0) + 1
    for name in sorted(per_doc):
        print(f"  {per_doc[name]:>3}  {name}")

    # --- 5 random chunks for the eyeball test ---
    print("\n" + "=" * 70)
    print("5 RANDOM CHUNKS (read each: self-contained? substantive? clean?)")
    print("=" * 70)
    rng = random.Random(SEED)
    for n, r in enumerate(rng.sample(records, 5), 1):
        wc = len(r["text"].split())
        print(f"\n--- sample {n} | id={r['id']} | {wc} words ---")
        print(r["text"])

    # --- persist for reuse ---
    CHUNKS_PREVIEW.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"\nWrote {len(records)} chunks to {CHUNKS_PREVIEW.name}")


if __name__ == "__main__":
    main()
