"""
Embedding + Vector Store + Retrieval for "The Unofficial Guide" (Project 1).

Implements the middle stages of the architecture in planning.md:

    Chunking --> Embedding + Vector Store --> Retrieval

Per the Retrieval Approach section of planning.md:
    embedding model = all-MiniLM-L6-v2 (via sentence-transformers)
    top-k          = 5
    vector store   = ChromaDB

Run:
    python embed_retrieve.py
"""

from __future__ import annotations

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import Chunk, chunk_documents_structured, load_documents

# --- Configuration (mirrors the Retrieval Approach section of planning.md) ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5
CHROMA_DIR = Path(__file__).parent / "chroma_db"   # persistent local store
COLLECTION_NAME = "unofficial_guide"

# Evaluation queries from the Evaluation Plan section of planning.md.
EVAL_QUERIES = [
    "Who should I look up if I am interested in machine learning courses in the IM program?",
    "Who is the MSIM Program Director?",
    "Which professor has significant consulting and industry experience reflected in their teaching?",
    "Which professors were recognized as Teachers Ranked Excellent in Spring 2025?",
    "Which professor specializes in information governance and privacy-related topics?",
]


def build_chunks() -> list[Chunk]:
    """Run the ingestion + chunking pipeline to get the chunks to index.

    Uses section-aware structured chunking (see README Failure Case Analysis).
    """
    documents = load_documents()
    return chunk_documents_structured(documents)


def build_index(
    chunks: list[Chunk],
    model: SentenceTransformer,
) -> chromadb.api.models.Collection.Collection:
    """Embed all chunks and store them (with metadata) in ChromaDB.

    The collection is created fresh each run so re-running the script does not
    accumulate duplicate entries. Cosine distance is used for similarity.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Start clean to keep the index in sync with the current corpus.
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c.text for c in chunks]
    ids = [c.chunk_id for c in chunks]
    metadatas = [
        {
            "source": Path(c.source).name,  # source document name
            "doc_id": c.doc_id,
            "chunk_index": int(c.chunk_id.split("::")[1]),  # position in document
            "start": c.start,
            "end": c.end,
        }
        for c in chunks
    ]

    # Encode locally with all-MiniLM-L6-v2, then hand the vectors to Chroma.
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True,
    ).tolist()

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return collection


def retrieve(
    query: str,
    collection,
    model: SentenceTransformer,
    top_k: int = TOP_K,
) -> list[dict]:
    """Retrieve the top-k most relevant chunks for ``query``.

    Returns a list of dicts containing the chunk text, its metadata, and the
    cosine distance score (lower = more similar).
    """
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )

    hits: list[dict] = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({"text": text, "metadata": meta, "distance": dist})
    return hits


def _print_hits(query: str, hits: list[dict]) -> None:
    print(f"\n{'=' * 78}\nQUERY: {query}\n{'=' * 78}")
    for rank, hit in enumerate(hits, start=1):
        meta = hit["metadata"]
        snippet = hit["text"].replace("\n", " ").strip()
        if len(snippet) > 200:
            snippet = snippet[:200] + " ..."
        print(
            f"\n[{rank}] distance={hit['distance']:.4f}  "
            f"source={meta['source']}  chunk_index={meta['chunk_index']}"
        )
        print(f"    {snippet}")


def main() -> None:
    print("Loading and chunking documents ...")
    chunks = build_chunks()
    print(f"  {len(chunks)} chunks to index")

    print(f"Loading embedding model: {EMBEDDING_MODEL} ...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print("Embedding chunks and building ChromaDB index ...")
    collection = build_index(chunks, model)
    print(f"  indexed {collection.count()} chunks in '{COLLECTION_NAME}'")

    # Example retrieval over the evaluation queries.
    for query in EVAL_QUERIES:
        hits = retrieve(query, collection, model, top_k=TOP_K)
        _print_hits(query, hits)


if __name__ == "__main__":
    main()
