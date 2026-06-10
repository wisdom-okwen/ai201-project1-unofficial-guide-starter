"""Milestone 4 (part 1): embed the chunks and load them into ChromaDB.

Run:  .venv/bin/python build_index.py

Rebuilds the local ChromaDB collection from scratch: runs the M3 chunking
pipeline, embeds every chunk with all-MiniLM-L6-v2, and stores each chunk's
text + embedding + source metadata (filename, chunk position, source, url,
topic). The collection uses cosine distance so the scores match the 0-2 range
the Milestone 4 checkpoint talks about.
"""
from __future__ import annotations

import chromadb
from chromadb.config import Settings

from chunking import chunk_all
from config import CHROMA_DIR, COLLECTION_NAME
from embedding import embed, get_model
from ingest import load_documents


def get_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )


def build_index() -> chromadb.Collection:
    print(f"Loading embedding model and documents ...")
    model = get_model()
    documents = load_documents()
    records = chunk_all(documents, model)
    print(f"Chunked {len(documents)} documents into {len(records)} chunks")

    client = get_client()
    # start clean so re-running doesn't duplicate or stale-mix chunks
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    embeddings = embed([r["text"] for r in records]).tolist()
    collection.add(
        ids=[r["id"] for r in records],
        documents=[r["text"] for r in records],
        metadatas=[r["metadata"] for r in records],
        embeddings=embeddings,
    )
    print(f"Indexed {collection.count()} chunks into ChromaDB "
          f"collection '{COLLECTION_NAME}' at {CHROMA_DIR.name}/")
    return collection


if __name__ == "__main__":
    build_index()
