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
DATA_DIR = Path(__file__).parent / "documents"
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


# --- Structured (section-aware) chunking ---------------------------------------
# These structured-chunking helpers improve retrieval on the highly structured
# faculty documents. See the Failure Case Analysis in README.md for the before/
# after distances that motivated this. Two ideas:
#   1. Split on section boundaries (blank lines) instead of blind character
#      windows, so a chunk is a coherent section rather than a mix of fragments.
#   2. Prepend a "PROFESSOR: <name>" header to every chunk so the person's name
#      travels with their content and is not diluted or split away.
def extract_header(text: str) -> str:
    """Return a short identity header for a document (e.g. its PROFESSOR line)."""
    for line in text.splitlines():
        if line.startswith("PROFESSOR:"):
            return line.strip()
    return ""


def _split_sections(text: str) -> list[str]:
    """Split text into sections on blank lines, dropping empties."""
    return [s.strip() for s in text.split("\n\n") if s.strip()]


def chunk_text_by_section(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
    pack: bool = True,
) -> list[str]:
    """Chunk text along section (blank-line) boundaries.

    ``pack=True``  -> greedily combine sections up to ``chunk_size`` (good for
                      prose-like profiles, keeps related sections together).
    ``pack=False`` -> emit one chunk per section (good for directory listings,
                      so each faculty entry becomes its own focused chunk).

    Any single section longer than ``chunk_size`` falls back to the character
    window splitter so no content is lost.
    """
    sections = _split_sections(text)
    chunks: list[str] = []

    if not pack:
        for sec in sections:
            if len(sec) > chunk_size:
                chunks.extend(p for p, _, _ in chunk_text(sec, chunk_size, overlap))
            else:
                chunks.append(sec)
        return chunks

    buf = ""
    for sec in sections:
        if len(sec) > chunk_size:
            if buf:
                chunks.append(buf)
                buf = ""
            chunks.extend(p for p, _, _ in chunk_text(sec, chunk_size, overlap))
            continue
        if not buf:
            buf = sec
        elif len(buf) + 2 + len(sec) <= chunk_size:
            buf = f"{buf}\n\n{sec}"
        else:
            chunks.append(buf)
            buf = sec
    if buf:
        chunks.append(buf)
    return chunks


def chunk_documents_structured(
    documents: list[Document],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    """Section-aware chunking with per-document strategy and name headers.

    Directory-style documents are split one entry per chunk; everything else is
    packed by section. Each chunk is prefixed with the document's PROFESSOR
    header (when present) so the professor's name stays attached to the content.
    """
    all_chunks: list[Chunk] = []
    for doc in documents:
        is_directory = (
            "FacultyDirectory" in doc.text or doc.doc_id == "faculty_listing"
        )
        header = extract_header(doc.text)
        pieces = chunk_text_by_section(
            doc.text, chunk_size, overlap, pack=not is_directory
        )
        for i, piece in enumerate(pieces):
            text = piece
            if header and not piece.startswith(header):
                text = f"{header}\n\n{piece}"
            all_chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}::{i}",
                    doc_id=doc.doc_id,
                    source=doc.source,
                    text=text,
                    start=-1,  # section-based chunks are not contiguous offsets
                    end=-1,
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

    # Use the same section-aware chunking the retrieval pipeline uses.
    chunks = chunk_documents_structured(documents)

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
                f"CHUNK {c.chunk_id}  (len {len(c.text)})",
                c.text,
            )

    # 3) Total chunk count.
    print(f"\n{'=' * 70}")
    print(f"TOTAL CHUNKS: {len(chunks)}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
