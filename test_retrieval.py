"""Milestone 4 checkpoint: test retrieval on the evaluation-plan questions.

Run:  .venv/bin/python test_retrieval.py

For each question it prints the top-k chunks with their cosine distance and
source, so we can eyeball relevance BEFORE adding generation. Q5 is the
deliberate failure case (no answer exists in the corpus) -- we expect the top
distance there to be noticeably worse / off-topic.
"""
from __future__ import annotations

import textwrap

from config import TOP_K
from retrieve import get_collection, retrieve

# The 5 evaluation questions from planning.md (Q5 is the planted failure case).
EVAL_QUERIES = [
    "How to pay for a dining discount, and why avoid Jester City Limits?",
    "How much is the Flex Meal Plan and what do you get?",
    "Where can I study late at night near campus?",
    "Are the dorms cold, and what should I pack?",
    "How do I appeal a parking ticket at UT Austin?",  # failure case
]


def preview(text: str, width: int = 100) -> str:
    """First line (the source/topic header) + a short snippet of the body."""
    header, _, body = text.partition("\n")
    snippet = textwrap.shorten(body.replace("\n", " "), width=width, placeholder=" ...")
    return f"{header}\n      {snippet}"


def main() -> None:
    collection = get_collection()
    print(f"Collection '{collection.name}' has {collection.count()} chunks | top-k={TOP_K}\n")

    for i, query in enumerate(EVAL_QUERIES, 1):
        tag = "  (FAILURE CASE)" if i == 5 else ""
        print("=" * 90)
        print(f"Q{i}{tag}: {query}")
        print("=" * 90)
        for rank, hit in enumerate(retrieve(query, k=TOP_K, collection=collection), 1):
            flag = "  <-- weak (>0.5)" if hit.distance > 0.5 else ""
            print(f"\n  #{rank}  distance={hit.distance:.3f}{flag}  [{hit.metadata['filename']}]")
            print(f"      {preview(hit.text)}")
        print()


if __name__ == "__main__":
    main()
