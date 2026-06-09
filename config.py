"""Shared configuration for the Unofficial Guide RAG pipeline.

Values here mirror the decisions recorded in planning.md so the spec and the
code stay in sync. If you change a number here, update planning.md too.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCUMENTS_DIR = ROOT / "documents"
CHROMA_DIR = ROOT / "chroma_db"          # local ChromaDB persistence (gitignored)
CHUNKS_PREVIEW = ROOT / "chunks.json"    # inspection artifact written by build_chunks.py

# --- Embedding / retrieval (planning.md > Retrieval Approach) ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"     # local, 384-dim, ~256-token input cap
COLLECTION_NAME = "unofficial_guide"
TOP_K = 5

# --- Semantic chunking guardrails (planning.md > Chunking Strategy) ---
BREAKPOINT_PERCENTILE = 90   # a chunk boundary is cut where adjacent-unit cosine
                             # distance exceeds this percentile within a document
MAX_CHUNK_WORDS = 180        # ~256 tokens; the embedding model truncates past that
MIN_CHUNK_WORDS = 40         # smaller chunks are merged into a neighbor
