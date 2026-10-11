# Grounded Faculty Review Assistant

A retrieval-augmented generation (RAG) assistant for exploring UIUC iSchool faculty expertise and student-reported course experiences.

The system retrieves relevant passages from faculty profiles, directory entries, and student reviews, then generates answers grounded in the retrieved evidence. When the available context is insufficient, it declines to answer instead of guessing.

## Demo

- [Part 1 — Walkthrough](https://www.loom.com/share/6d8dd7d564ea4a3c8b6d226a8c3a900d)
- [Part 2 — Walkthrough](https://www.loom.com/share/e59bab63dc1d4b2b8788f7a94e9eec29)

## Why this project

Information about faculty research areas, teaching experiences, and course expectations is scattered across official university pages and student review sites.

This project combines these sources into a searchable knowledge base so students can ask natural-language questions and receive concise answers with the supporting source documents.

Student reviews are subjective and incomplete, so the system treats them as supplementary context rather than authoritative facts.

## Key capabilities

- Semantic search over faculty profiles and student reviews
- Section-aware document chunking
- Local embedding generation with `all-MiniLM-L6-v2`
- Cosine-similarity retrieval through ChromaDB
- Grounded answer generation with Groq-hosted Llama 3.3
- Programmatic source attribution based on retrieval metadata
- Explicit refusal when the retrieved context does not support an answer

## Architecture

```text
Source documents
      │
      ▼
Cleaning and section-aware chunking
      │
      ▼
Normalized embeddings
      │
      ▼
Persistent ChromaDB index
      │
      ▼
User query → top-k semantic retrieval
      │
      ▼
Context-only LLM prompt
      │
      ▼
Answer + retrieved source list
```

## Data sources

The corpus combines three types of public sources:

- Student reviews from Rate My Professors
- UIUC iSchool faculty profiles and the faculty directory
- The iSchool's “Teachers Ranked Excellent” announcement

The collected documents cover faculty research areas, professional backgrounds, teaching-related comments, and selected academic recognitions.

## Technical design

### Document ingestion and chunking

The source files are stored as plain-text documents. Preprocessing performs light normalization:

- Normalize line endings
- Remove trailing whitespace
- Collapse repeated blank lines
- Preserve blank-line boundaries between logical sections

The final chunking strategy is section-aware:

- Faculty directory entries are split one professor per chunk
- Faculty profiles and reviews are packed by section up to approximately 1,000 characters
- A 150-character overlap is used when an individual section exceeds the target size
- Each chunk is prefixed with a `PROFESSOR: <name>` header so the professor identity remains attached to the content

This approach keeps related information together and prevents a single directory chunk from mixing information from many professors.

### Embeddings and retrieval

The system uses `all-MiniLM-L6-v2` through Sentence Transformers. Embeddings are generated locally, normalized, and stored in ChromaDB with cosine distance.

For each query, the system retrieves the top five chunks together with metadata such as:

- Source filename
- Document identifier
- Chunk position
- Character offsets
- Cosine distance

The index is rebuilt from the current document corpus each time the embedding pipeline runs, preventing stale or duplicated entries.

### Grounded generation

Retrieved chunks are the only context passed to the language model. The generation prompt instructs the model to:

1. Answer only from the supplied context
2. Avoid using prior knowledge or inventing facts
3. Return exactly `I don't have enough information on that.` when the evidence is insufficient
4. Keep the answer concise and specific

The Gradio interface displays the answer together with a de-duplicated source list.

The source list is generated from ChromaDB metadata rather than from the model's response, which prevents the model from fabricating citations.

## Evaluation

The system was tested with five representative queries covering research expertise, program information, professional experience, academic recognition, and privacy-related research.

| Query type | Result | Interpretation |
|---|---|---|
| Machine learning expertise | Accurate | Retrieved the relevant faculty profile |
| MSIM program director | Correct refusal | The answer existed in the corpus, but the supporting chunk was not retrieved |
| Consulting and industry experience | Accurate | Retrieved the relevant professional background |
| Teachers Ranked Excellent recognition | Partially complete | The retrieval results contained relevant faculty, but the answer missed part of the expected list |
| Information governance and privacy | Accurate after refinement | Retrieved the correct faculty entry after improving the corpus and chunking |

The evaluation showed that the grounding behavior was effective at preventing unsupported answers. It also showed that retrieval quality, especially corpus coverage and chunk structure, was the main bottleneck.

## Retrieval failure and fix

One test query asked:

> Which professor specializes in information governance and privacy-related topics?

### Before the fix

The correct professor was Madelyn Sanfilippo, but the system ranked Karen Wickett's profile first.

| Rank | Source | Distance |
|---|---|---:|
| 1 | Karen Wickett profile | 0.4647 |
| 2 | Faculty directory entry for Madelyn Sanfilippo | 0.5080 |

Two issues contributed to the failure:

1. Madelyn's relevant research area appeared only in one line of the faculty directory. There was no dedicated profile containing the same terminology.
2. The directory had been split using blind character windows, so one chunk combined information from multiple professors. This diluted the signal for Madelyn's entry.

The failure was caused by retrieval quality rather than by a phrase being cut at a chunk boundary. The existing overlap already preserved the relevant text.

### After the fix

Two changes were applied:

1. Added a dedicated Madelyn Sanfilippo profile assembled from the available public sources
2. Replaced blind directory chunking with section-aware chunking and professor-prefixed metadata

| Rank | Source | Distance |
|---|---|---:|
| 1 | Madelyn entry in the faculty directory | 0.2272 |
| 2 | Dedicated Madelyn profile | 0.2826 |
| 5 | Karen Wickett profile | 0.4802 |

The correct result moved from rank 2 to rank 1, and its cosine distance improved from `0.508` to `0.227`.

The comparison can be reproduced with:

```bash
python compare_chunking.py
```

## Running locally

### 1. Clone the repository

```bash
git clone https://github.com/AnniecTW/grounded-faculty-review-rag.git
cd grounded-faculty-review-rag
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Groq API key

```bash
cp .env.example .env
```

Add your key to `.env`:

```text
GROQ_API_KEY=your_key_here
```

### 5. Build the embedding index

```bash
python embed_retrieve.py
```

### 6. Launch the Gradio interface

```bash
python rag.py
```

To run the evaluation queries from the command line:

```bash
python rag.py --cli
```

## Project structure

```text
.
├── documents/          # Plain-text source documents
├── ingest.py           # Cleaning and structured chunking
├── embed_retrieve.py   # Embeddings, ChromaDB indexing, retrieval
├── rag.py              # Grounded generation and Gradio interface
├── compare_chunking.py # Before-and-after retrieval comparison
├── requirements.txt
└── .env.example
```

## Limitations and next steps

The current system is a small prototype, so several improvements remain:

- Expand and regularly refresh the source corpus
- Add metadata filtering for professor names and source types
- Compare semantic retrieval with hybrid keyword-plus-vector retrieval
- Evaluate a reranking model for ambiguous queries
- Track metrics such as Recall@k, MRR, and answer support rate
- Add a larger evaluation set with manually verified expected answers
- Handle conflicting or outdated student reviews more explicitly

## Project origin

This project began with an AI201 starter repository and was independently extended with structured document processing, retrieval implementation, grounded generation, evaluation, and failure analysis.
