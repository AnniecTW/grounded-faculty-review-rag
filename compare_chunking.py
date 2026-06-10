"""
Before/after retrieval comparison for the failing evaluation query.

BEFORE: original character-window chunking, no Madelyn profile.
AFTER : section-aware structured chunking + added Madelyn profile.

Uses an in-memory ChromaDB so the persistent chroma_db/ is untouched.

Run:
    python compare_chunking.py
"""

from __future__ import annotations

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import chunk_documents, chunk_documents_structured, load_documents

QUERY = "Which professor specializes in information governance and privacy-related topics?"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TARGET = "Madelyn Sanfilippo"


def index_and_query(chunks, model, client, name):
    col = client.create_collection(name, metadata={"hnsw:space": "cosine"})
    embeddings = model.encode(
        [c.text for c in chunks], normalize_embeddings=True
    ).tolist()
    col.add(
        ids=[c.chunk_id for c in chunks],
        documents=[c.text for c in chunks],
        embeddings=embeddings,
        metadatas=[
            {
                "source": Path(c.source).name,
                "chunk_index": int(c.chunk_id.split("::")[1]),
            }
            for c in chunks
        ],
    )
    res = col.query(query_embeddings=model.encode([QUERY], normalize_embeddings=True).tolist(), n_results=5)
    return res


def _print_results(title, res):
    print(f"\n{title}")
    print("-" * 78)
    print(f"{'rank':<5}{'distance':<11}{'source':<34}{'chunk'}")
    target_rank = None
    for i, (meta, dist, doc) in enumerate(
        zip(res["metadatas"][0], res["distances"][0], res["documents"][0]), start=1
    ):
        mark = ""
        if TARGET in doc or "sanfilippo" in meta["source"].lower():
            mark = "  <-- TARGET (Madelyn)"
            if target_rank is None:
                target_rank = i
        print(f"{i:<5}{dist:<11.4f}{meta['source']:<34}{meta['chunk_index']}{mark}")
    if target_rank:
        print(f"==> Madelyn first appears at rank {target_rank}")
    else:
        print("==> Madelyn NOT in top-5")


def main():
    print(f"QUERY: {QUERY}\n")
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.EphemeralClient()  # in-memory; does not touch chroma_db/

    docs_all = load_documents()
    docs_before = [d for d in docs_all if d.doc_id != "profile_madelyn_sanfilippo"]

    before = index_and_query(chunk_documents(docs_before), model, client, "before")
    after = index_and_query(
        chunk_documents_structured(docs_all), model, client, "after"
    )

    _print_results("BEFORE  (char-window chunking, no Madelyn profile)", before)
    _print_results("AFTER   (section-aware chunking + Madelyn profile)", after)


if __name__ == "__main__":
    main()
