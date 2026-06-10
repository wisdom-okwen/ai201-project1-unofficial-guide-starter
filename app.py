"""Milestone 5: Gradio query interface for The Unofficial Guide.

Run:  .venv/bin/python app.py
Then open http://localhost:7860

Type a question -> the system retrieves relevant chunks, generates a grounded
answer with Groq, and shows which source document(s) it drew from. Questions the
guides don't cover return an explicit "I don't have enough information" with no
sources.
"""
from __future__ import annotations

import gradio as gr

from generate import ask
from ingest import load_documents

# filename -> "Source title (url)" for a friendlier "Retrieved from" panel
_LABELS: dict[str, str] = {}
for _doc in load_documents():
    _src = _doc.metadata.get("source", "").split(" (")[0].strip()
    _url = _doc.metadata.get("url", "").strip()
    _LABELS[_doc.filename] = f"{_src} ({_url})" if _url else _src

EXAMPLES = [
    "Which dining hall is all-you-can-eat, and how do I get a meal discount?",
    "How much does the Flex Meal Plan cost?",
    "Where can I study late at night near campus?",
    "Are the dorms cold? What should I pack?",
    "How do I appeal a parking ticket at UT Austin?",  # not covered -> declines
]


def handle_query(question: str):
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""
    result = ask(question)
    if result["sources"]:
        sources = "\n".join(f"• {s} — {_LABELS.get(s, '')}" for s in result["sources"])
    else:
        sources = "— (no sources: the guides don't cover this)"
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide — UT Austin") as demo:
    gr.Markdown(
        "# The Unofficial Guide — UT Austin\n"
        "Ask about UT Austin student life (dorms, dining, studying, getting "
        "around, packing). Answers come **only** from real student/alumni guides, "
        "and every answer shows its sources."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. Which dining hall is all-you-can-eat?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    gr.Examples(examples=EXAMPLES, inputs=inp)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
