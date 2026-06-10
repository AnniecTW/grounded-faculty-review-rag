"""
Grounded RAG + Gradio interface for "The Unofficial Guide" (Project 1).

Final stage of the architecture in planning.md:

    Retrieval (ChromaDB, top-k) --> Generation (Groq) --> Answer + Sources

- Reuses the existing retrieval function from embed_retrieve.py.
- Sends retrieved chunks to Groq's llama-3.3-70b-versatile with a grounding
  prompt that forbids answering beyond the provided context.
- Source filenames are derived programmatically from retrieval metadata, never
  from the model's text.

Prereq: run `python embed_retrieve.py` once so chroma_db/ exists.

Run:
    python rag.py            # launch the Gradio app
    python rag.py --cli      # quick terminal test over the eval queries
"""

from __future__ import annotations

import sys

import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

from embed_retrieve import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    EVAL_QUERIES,
    TOP_K,
    retrieve,
)

GROQ_MODEL = "llama-3.3-70b-versatile"
INSUFFICIENT = "I don't have enough information on that."

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about Information "
    "Management professors at the University of Illinois Urbana-Champaign.\n"
    "Follow these rules strictly:\n"
    "1. Answer ONLY using the information in the provided context.\n"
    "2. Do not use any prior knowledge or make up facts.\n"
    "3. If the context does not contain enough information to answer the "
    f'question, reply with exactly this sentence: "{INSUFFICIENT}"\n'
    "4. Be concise and specific, and base every claim on the context."
)

# --- Load resources once (model, vector store, Groq client) --------------------
load_dotenv()  # reads GROQ_API_KEY from .env
_model = SentenceTransformer(EMBEDDING_MODEL)
_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
try:
    _collection = _client.get_collection(COLLECTION_NAME)
except Exception as exc:  # collection missing -> guide the user
    raise SystemExit(
        f"Could not open collection '{COLLECTION_NAME}'. "
        "Run `python embed_retrieve.py` first to build the index.\n"
        f"({exc})"
    )
_groq = Groq()  # picks up GROQ_API_KEY from the environment


def build_context(hits: list[dict]) -> str:
    """Format retrieved chunks into a labeled context block for the prompt."""
    blocks = []
    for i, hit in enumerate(hits, start=1):
        source = hit["metadata"]["source"]
        blocks.append(f"[{i}] (source: {source})\n{hit['text']}")
    return "\n\n".join(blocks)


def unique_sources(hits: list[dict]) -> list[str]:
    """Source filenames from retrieval metadata, de-duplicated, in rank order."""
    seen: list[str] = []
    for hit in hits:
        src = hit["metadata"]["source"]
        if src not in seen:
            seen.append(src)
    return seen


def answer_question(question: str, top_k: int = TOP_K) -> dict:
    """Run the full grounded RAG pipeline for a single question.

    Returns {"answer": str, "sources": list[str]}.
    """
    question = (question or "").strip()
    if not question:
        return {"answer": "Please enter a question.", "sources": []}

    # 1) Retrieval (reuses the existing function over the persisted collection).
    hits = retrieve(question, _collection, _model, top_k=top_k)
    context = build_context(hits)

    # 2) Generation, grounded in the retrieved context only.
    completion = _groq.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0,  # deterministic, reduces drift from the context
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            },
        ],
    )
    answer = completion.choices[0].message.content.strip()

    # 3) Source attribution computed from metadata, not from the model.
    #    If the model reports insufficient context, attribute no sources.
    if answer.lower().startswith(INSUFFICIENT.lower().rstrip(".")):
        sources: list[str] = []
    else:
        sources = unique_sources(hits)

    return {"answer": answer, "sources": sources}


# --- Gradio interface -----------------------------------------------------------
def _gradio_fn(question: str):
    result = answer_question(question)
    sources = result["sources"]
    sources_md = (
        "\n".join(f"- {s}" for s in sources) if sources else "_(no sources)_"
    )
    return result["answer"], sources_md


def build_app():
    import gradio as gr

    return gr.Interface(
        fn=_gradio_fn,
        inputs=gr.Textbox(
            label="Question",
            placeholder="e.g. Which professor specializes in privacy and governance?",
            lines=2,
        ),
        outputs=[
            gr.Textbox(label="Answer", lines=6),
            gr.Markdown(label="Sources"),
        ],
        title="The Unofficial Guide — UIUC IM Professors",
        description=(
            "Grounded RAG over student reviews and faculty profiles. "
            "Answers come only from retrieved documents; sources are listed below."
        ),
        examples=[[q] for q in EVAL_QUERIES],
    )


def _cli() -> None:
    for q in EVAL_QUERIES:
        result = answer_question(q)
        print(f"\n{'=' * 78}\nQ: {q}\n{'-' * 78}")
        print(f"A: {result['answer']}")
        print(f"Sources: {', '.join(result['sources']) or '(none)'}")


if __name__ == "__main__":
    if "--cli" in sys.argv:
        _cli()
    else:
        build_app().launch()
