"""Document ingestion: load the .txt guides, split off their source header, and
clean the body.

Each file in documents/ begins with a small "Key: value" header block
(Source / URL / Topic / University / ...), then a blank line, then the body.
We keep the header metadata for citation and prepend a short version of it to
every chunk (see chunking.py), so a retrieved chunk always knows where it came
from.

The bodies were already cleaned of nav/ads when collected, so clean_body() is a
light normaliser (entity decode, stray-tag strip, whitespace) that also acts as
a safeguard if a messier source is added later.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field

from config import DOCUMENTS_DIR

_HEADER_LINE = re.compile(r"^([A-Za-z][A-Za-z ]+):\s+(.*)$")
_HTML_TAG = re.compile(r"<[^>]+>")
_MANY_BLANKS = re.compile(r"\n{3,}")


@dataclass
class Document:
    filename: str
    metadata: dict[str, str]
    body: str
    # short, human-readable provenance line prepended to each chunk
    header_prefix: str = field(default="")


def _short(value: str) -> str:
    """Trim a long header value down to its leading label.

    'Her Campus (Texas) — "A Comparison..."'  -> 'Her Campus (Texas)'
    'General campus survival (resources...)'  -> 'General campus survival'
    """
    value = re.split(r"\s+[—-]\s+", value)[0]   # cut at an em/en dash separator
    value = value.split(" (")[0]                # cut a trailing parenthetical
    return value.strip()


def parse_header(text: str) -> tuple[dict[str, str], str]:
    """Split the leading 'Key: value' header block from the document body."""
    lines = text.splitlines()
    metadata: dict[str, str] = {}
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "":               # blank line ends the header block
            body_start = i + 1
            break
        m = _HEADER_LINE.match(line.strip())
        if m:
            metadata[m.group(1).strip().lower()] = m.group(2).strip()
        else:                                 # not a header line -> body starts here
            body_start = i
            break
    body = "\n".join(lines[body_start:])
    return metadata, body


def clean_body(body: str) -> str:
    """Light normalisation; safeguard against HTML if a raw source slips in."""
    body = html.unescape(body)               # &amp; -> &, &nbsp; -> space, etc.
    body = _HTML_TAG.sub("", body)           # strip any leftover tags
    body = _MANY_BLANKS.sub("\n\n", body)    # collapse runs of blank lines
    return body.strip()


def load_documents() -> list[Document]:
    """Load and clean every documents/*.txt file."""
    docs: list[Document] = []
    for path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        metadata, body = parse_header(raw)
        body = clean_body(body)
        source = metadata.get("source", path.stem)
        topic = metadata.get("topic", "")
        prefix = f"[Source: {_short(source)} | Topic: {_short(topic)}]"
        docs.append(
            Document(
                filename=path.name,
                metadata=metadata,
                body=body,
                header_prefix=prefix,
            )
        )
    return docs


if __name__ == "__main__":
    # Quick manual check: load everything and print the first cleaned document.
    documents = load_documents()
    print(f"Loaded {len(documents)} documents\n")
    first = documents[0]
    print(f"--- {first.filename} ---")
    print(f"metadata: {first.metadata}")
    print(f"prefix:   {first.header_prefix}")
    print(f"body chars: {len(first.body)}\n")
    print(first.body[:800])
