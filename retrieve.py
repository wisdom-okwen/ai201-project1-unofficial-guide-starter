"""Milestone 4 (part 2): semantic retrieval over the ChromaDB collection.

retrieve(query, k) embeds the query with the same model used at index time and
returns the top-k chunks with their source metadata and cosine distance (lower
is more similar).
"""
from __future__ import annotations

from dataclasses import dataclass

from build_index import get_client
from config import COLLECTION_NAME, TOP_K
from embedding import embed


@dataclass
class Hit:
    text: str
    distance: float
    metadata: dict

    @property
    def source(self) -> str:
        return self.metadata.get("source", self.metadata.get("filename", "unknown"))


def get_collection():
    return get_client().get_collection(COLLECTION_NAME)


def retrieve(query: str, k: int = TOP_K, collection=None) -> list[Hit]:
    collection = collection or get_collection()
    query_embedding = embed([query]).tolist()
    result = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        Hit(text=doc, distance=dist, metadata=meta)
        for doc, meta, dist in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]
