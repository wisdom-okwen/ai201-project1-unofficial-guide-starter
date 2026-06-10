"""Shared embedding model.

One place loads all-MiniLM-L6-v2 so the *same* model (and vector space) is used
everywhere: sentence embeddings during chunking, chunk embeddings at index time,
and query embeddings at search time. The model is cached so repeated calls in a
process don't reload it.
"""
from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def embed(texts: list[str], normalize: bool = True):
    """Embed a list of texts into L2-normalised vectors (numpy array)."""
    return get_model().encode(texts, normalize_embeddings=normalize)
