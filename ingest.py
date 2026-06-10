"""
Ingestion pipeline for "The Unofficial Guide" (Project 1).

Implements the first two stages of the architecture described in planning.md:

    Source Documents (.txt) --> Document Ingestion --> Chunking

Chunking follows the Chunking Strategy section of planning.md exactly:
    chunk size = 1000 characters, overlap = 150 characters.

Run:
    python ingest.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# --- Configuration (mirrors the Chunking Strategy section of planning.md) ---
DATA_DIR = Path(__file__).parent / "data"
CHUNK_SIZE = 1000      # characters
CHUNK_OVERLAP = 150    # characters


# --- Consistent document format -------------------------------------------------
@dataclass
class Document:
    """A single source document loaded from disk."""

    doc_id: str                       # stable id (the file name without extension)
    source: str                       # original file path, used for attribution
    text: str                         # cleaned text content
    metadata: dict = field(default_factory=dict)


@dataclass
class Chunk:
    """A contiguous slice of a document's text."""

    chunk_id: str                     # "<doc_id>::<index>"
    doc_id: str                       # parent document id
    source: str                       # parent source path (attribution)
    text: str                         # the chunk text
    start: int                        # start offset in the cleaned document
    end: int                          # end offset (exclusive) in the cleaned document


# --- Stage 1: Document loading --------------------------------------------------
def load_documents(data_dir: Path = DATA_DIR) -> list[Document]:
    """Load every .txt file in ``data_dir`` into a Document.

    Files are read as UTF-8 and sorted by name so output is deterministic.
    """
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    documents: list[Document] = []
    for path in sorted(data_dir.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        cleaned = clean_text(raw)
        if not cleaned:
            # Skip empty/whitespace-only files rather than embedding noise.
            continue
        documents.append(
            Document(
                doc_id=path.stem,
                source=str(path),
                text=cleaned,
                metadata={"file_name": path.name, "char_count": len(cleaned)},
            )
        )
    return documents


# --- Cleaning -------------------------------------------------------------------
def clean_text(text: str) -> str:
    """Normalize whitespace while preserving the document's logical structure.

    The source .txt files are already plain text (no HTML), so cleaning is light:
      * normalize Windows/Mac line endings to "\n"
      * strip trailing spaces/tabs from every line
      * collapse 3+ consecutive blank lines down to a single blank line
      * strip leading/trailing whitespace from the whole document

    Blank lines between sections (e.g. RESEARCH AREAS / BIOGRAPHY) are kept so
    that section boundaries remain readable inside chunks.
    """
    # Normalize line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Strip trailing whitespace on each line.
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Collapse runs of 3+ newlines into exactly two (one blank line).
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# --- Stage 2: Chunking ----------------------------------------------------------
def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[tuple[str, int, int]]:
    """Split text into overlapping fixed-size character windows.

    Implements the planning.md strategy: 1000-character chunks with 150-character
    overlap. The window advances by ``chunk_size - overlap`` (= 850) characters,
    so each chunk shares its final 150 characters with the next one.

    Returns a list of (chunk_text, start_offset, end_offset) tuples.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    step = chunk_size - overlap
    chunks: list[tuple[str, int, int]] = []

    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        piece = text[start:end]
        chunks.append((piece, start, end))
        if end == n:
            break
        start += step

    return chunks


def chunk_documents(
    documents: list[Document],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    """Apply :func:`chunk_text` to every document, carrying attribution forward."""
    all_chunks: list[Chunk] = []
    for doc in documents:
        for i, (piece, start, end) in enumerate(
            chunk_text(doc.text, chunk_size, overlap)
        ):
            all_chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}::{i}",
                    doc_id=doc.doc_id,
                    source=doc.source,
                    text=piece,
                    start=start,
                    end=end,
                )
            )
    return all_chunks


# --- Demonstration output -------------------------------------------------------
def _preview(label: str, body: str) -> None:
    print(f"\n{'=' * 70}\n{label}\n{'=' * 70}")
    print(body)


def main() -> None:
    documents = load_documents()
    print(f"Loaded {len(documents)} documents from {DATA_DIR}")

    chunks = chunk_documents(documents)

    # 1) One cleaned document.
    sample_doc = documents[0]
    _preview(
        f"CLEANED DOCUMENT: {sample_doc.doc_id} "
        f"({sample_doc.metadata['char_count']} chars)",
        sample_doc.text,
    )

    # 2) Five representative chunks (evenly spaced across the whole corpus).
    if chunks:
        count = min(5, len(chunks))
        step = max(1, len(chunks) // count)
        representative = [chunks[i * step] for i in range(count)]
        for c in representative:
            _preview(
                f"CHUNK {c.chunk_id}  (chars {c.start}-{c.end}, len {len(c.text)})",
                c.text,
            )

    # 3) Total chunk count.
    print(f"\n{'=' * 70}")
    print(f"TOTAL CHUNKS: {len(chunks)}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
