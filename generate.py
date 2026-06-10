"""Milestone 5: grounded answer generation.

ask(question) ties the whole pipeline together:
  retrieve top-k chunks  ->  build a grounded prompt  ->  Groq LLM  ->  answer.

Grounding is enforced two ways so the model can't fall back on training
knowledge:
  1. A strict system prompt: answer ONLY from the provided context, and reply
     with an exact decline sentence when the context is insufficient.
  2. Source attribution is built programmatically from the retrieved chunks'
     metadata -- it is never left to the model to invent. When the model
     declines, we return no sources (nothing relevant was actually used).
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq

from config import TOP_K
from retrieve import retrieve

load_dotenv()

LLM_MODEL = "llama-3.3-70b-versatile"
DECLINE = "I don't have enough information on that."
# cosine-distance cutoff for deciding a chunk is genuinely relevant (matches the
# Milestone 4 observation that good matches sit well below 0.5)
RELEVANCE_THRESHOLD = 0.5

SYSTEM_PROMPT = (
    "You are The Unofficial Guide, a question-answering assistant for University "
    "of Texas at Austin students. Answer the question using ONLY the information "
    "in the context documents provided by the user. Rules:\n"
    "- Use only facts stated in the context. Do NOT use outside or prior knowledge.\n"
    "- Do NOT guess, extrapolate, or add general advice.\n"
    f'- If the context does not contain enough information to answer, reply with '
    f'EXACTLY this sentence and nothing else: "{DECLINE}"\n'
    "- Otherwise, answer concisely and cite the source filename(s) you used in "
    "parentheses, e.g. (source: 03_meal_plans.txt)."
)

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key or api_key == "your_key_here":
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your "
                "free key from https://console.groq.com"
            )
        _client = Groq(api_key=api_key)
    return _client


def _build_context(hits) -> str:
    blocks = []
    for hit in hits:
        blocks.append(f"(source: {hit.metadata['filename']})\n{hit.text}")
    return "\n\n---\n\n".join(blocks)


def ask(question: str, k: int = TOP_K) -> dict:
    """Return {'answer': str, 'sources': list[str], 'hits': list[Hit]}."""
    hits = retrieve(question, k=k)
    relevant = [h for h in hits if h.distance < RELEVANCE_THRESHOLD]

    # Nothing relevant was retrieved -> decline deterministically without spending
    # an LLM call or risking a hallucinated answer (this is the Q5 failure case).
    if not relevant:
        return {"answer": DECLINE, "sources": [], "hits": hits}

    user_prompt = (
        f"Context documents:\n\n{_build_context(relevant)}\n\n"
        f"Question: {question}"
    )
    response = _get_client().chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    answer = response.choices[0].message.content.strip()

    # Programmatic attribution: unique source files of the relevant chunks, in
    # rank order. If the model declined, surface no sources.
    sources: list[str] = []
    if DECLINE.rstrip(".") not in answer:
        for hit in relevant:
            name = hit.metadata["filename"]
            if name not in sources:
                sources.append(name)

    return {"answer": answer, "sources": sources, "hits": hits}


if __name__ == "__main__":
    # End-to-end grounding test on a few queries, incl. the uncovered one.
    tests = [
        "How much does the optional Flex Meal Plan cost and what do you get?",
        "Are the UT dorms cold, and what should I pack because of it?",
        "Why should I avoid Jester City Limits?",
        "How do I appeal a parking ticket at UT Austin?",  # not in the corpus
    ]
    for q in tests:
        result = ask(q)
        print("=" * 80)
        print("Q:", q)
        print("A:", result["answer"])
        print("Sources:", result["sources"] or "(none)")
        print()
