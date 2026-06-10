# The Unofficial Guide — Project 1

A retrieval-augmented generation (RAG) system that answers questions about
Information Management professors at the University of Illinois Urbana-Champaign,
grounded in student reviews and faculty profiles.

## Demo Videos

Two Loom walkthroughs introducing the project:

- [Part 1 — Walkthrough](https://www.loom.com/share/6d8dd7d564ea4a3c8b6d226a8c3a900d)
- [Part 2 — Walkthrough](https://www.loom.com/share/e59bab63dc1d4b2b8788f7a94e9eec29)

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

Student reviews of selected Information Management professors at the University of
Illinois Urbana-Champaign. The system surfaces insight into professors' teaching and
grading styles to help IM students — and students from other programs considering IM
courses — make more informed course-selection decisions. This knowledge is valuable but
hard to find through official channels because it is scattered across review sites and
faculty pages. Gathering the relevant pages and passages into one knowledge base makes
the information easier to access and lets the system generate more comprehensive answers.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| #   | Source | Type | URL or file path |
| --- | ------ | ---- | ---------------- |
| 1   | Jingrui He | Rate My Professors | https://www.ratemyprofessors.com/professor/2766039 |
| 2   | Yoo-Seong Song | Rate My Professors | https://www.ratemyprofessors.com/professor/1861158 |
| 3   | Kevin Trainor | Rate My Professors | https://www.ratemyprofessors.com/professor/1861162 |
| 4   | John Weible | Rate My Professors | https://www.ratemyprofessors.com/professor/1861164 |
| 5   | Karen Wickett | Rate My Professors | https://www.ratemyprofessors.com/professor/1861165 |
| 6   | Martin Wolske | Rate My Professors | https://www.ratemyprofessors.com/professor/1861166 |
| 7   | Brandon Batzloff | Rate My Professors | https://www.ratemyprofessors.com/professor/2924903 |
| 8   | Madelyn Sanfilippo | Rate My Professors | https://www.ratemyprofessors.com/professor/2827901 |
| 9   | Jingrui He | Faculty profile | https://ischool.illinois.edu/people/jingrui-he |
| 10  | Yoo-Seong Song | Faculty profile | https://ischool.illinois.edu/people/yoo-seong-song |
| 11  | Karen Wickett | Faculty profile | https://ischool.illinois.edu/people/karen-wickett |
| 12  | David Charles | Faculty profile | https://ischool.illinois.edu/people/david-charles |
| 13  | Renee Hendricks | Faculty profile | https://ischool.illinois.edu/people/renee-hendricks |
| 14  | iSchool Faculty Directory | Faculty directory | https://ischool.illinois.edu/people/faculty |
| 15  | Teachers Ranked Excellent (Spring 2025) | News article | https://ischool.illinois.edu/news-events/news/2025/09/record-number-instructors-ranked-excellent |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** ~1000 characters.

**Overlap:** 150 characters.

**Why these choices fit your documents:** The corpus is short, highly structured text
(faculty profiles, review pages, a directory listing), so chunking is section-aware rather
than blind character windows (`chunk_documents_structured` in `ingest.py`). The faculty
directory is split one entry per chunk so each professor's listing stays a focused,
self-contained chunk; profiles and reviews are packed along blank-line section boundaries
up to ~1000 characters; and each chunk is prefixed with a `PROFESSOR: <name>` header so the
professor's name travels with its content. The 150-character overlap is a fallback for any
single section longer than the chunk size. Preprocessing is light: the source files are
already plain text, so cleaning only normalizes line endings, strips trailing whitespace,
and collapses repeated blank lines.

**Final chunk count:** 66 chunks across 16 documents.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via sentence-transformers, run locally. Embeddings are
normalized and stored in ChromaDB with cosine distance; retrieval returns the top 5 chunks
per query. The model offers a good balance of retrieval quality and efficiency for a
relatively small corpus.

**Production tradeoff reflection:** Deploying this for real users with no cost constraint, I
would consider a larger, more accurate embedding model. The factors I would weigh most are
retrieval accuracy on educational and course-related text and the ability to correctly
associate professors, courses, and reviews. Multilingual support matters less here because
the corpus is English content about a U.S. university. Latency would still be a
consideration, but I would prioritize retrieval quality over speed.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** Generation uses Groq's `llama-3.3-70b-versatile`
at `temperature=0`. The retrieved chunks are the only context placed in the prompt, and the
system prompt instructs the model to: (1) answer only from the provided context, (2) use no
prior knowledge and invent no facts, and (3) reply with exactly
`"I don't have enough information on that."` when the context is insufficient. Question 2 in
the evaluation below shows this working — the model declines rather than guessing when the
supporting chunk is not retrieved.

**How source attribution is surfaced in the response:** The source list is computed
programmatically from retrieval metadata — the source filenames come from ChromaDB, not from
the model's text — so citations cannot be fabricated. The Gradio interface shows the answer
and, below it, the de-duplicated list of source filenames the answer was drawn from. When the
model reports insufficient context, no sources are listed.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| #   | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
| --- | -------- | --------------- | ---------------------------- | ----------------- | ----------------- |
| 1   | Who to look up for machine learning courses in the IM program? | Jingrui He | Identifies Jingrui He as a machine learning / data mining expert | Relevant | Accurate |
| 2   | Who is the MSIM Program Director? | Jingrui He | "I don't have enough information on that." | Off-target | Correct refusal (grounded — see note) |
| 3   | Which professor has significant consulting / industry experience? | Yoo-Seong Song | Yoo-Seong Song (former Ernst & Young and Accenture consultant) | Relevant | Accurate |
| 4   | Which professors were Teachers Ranked Excellent in Spring 2025? | Jingrui He, Yoo-Seong Song, Kevin Trainor, John Weible, Karen Wickett (among others) | He, Song, Wickett, Sanfilippo, Weible | Relevant | Partially accurate |
| 5   | Which professor specializes in information governance and privacy? | Madelyn Sanfilippo | Madelyn Sanfilippo | Relevant | Accurate |

> **Note on Q2:** The answer (Jingrui He) does exist in the corpus, in
> `profile_jingrui_he.txt` ("TITLE: Professor and MSIM Program Director"), but that chunk
> was not retrieved into the top-5, so it never reached the model. Given the context it
> actually received, the model behaved correctly by declining rather than guessing — this is
> grounding working as intended, with the gap on the retrieval side.

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

"Which professor specializes in information governance and privacy-related topics?"
Expected answer: **Madelyn Sanfilippo**.

**What the system returned:**

The top-ranked chunk was **Karen Wickett**'s profile (her RESEARCH AREAS list), not
Madelyn Sanfilippo. The correct chunk was only retrieved at rank 2.

Before fix (character-window chunking, top-5):

| rank | distance | source                    | chunk                   |
| ---- | -------- | ------------------------- | ----------------------- |
| 1    | 0.4647   | profile_karen_wickett.txt | 0                       |
| 2    | 0.5080   | faculty_listing.txt       | 1 _(Madelyn — correct)_ |
| 3    | 0.5240   | faculty_listing.txt       | 0                       |
| 4    | 0.5415   | profile_david_charles.txt | 0                       |
| 5    | 0.5430   | profile_karen_wickett.txt | 3                       |

**Root cause (tied to a specific pipeline stage):**

Two stages combined:

1. **Data coverage** — There was no dedicated profile for Madelyn Sanfilippo. The
   only place in the corpus linking her to "Information Governance, Privacy, Policy"
   was a single line in `faculty_listing.txt`; the terms "governance"/"privacy"
   appeared nowhere else (not even in her own RMP reviews).
2. **Chunking (dilution, not splitting)** — `faculty_listing.txt` was chunked with
   blind character windows, so one chunk held ~10 professors. Madelyn's single line
   was diluted by everyone else's text, pushing the chunk's distance up to 0.508.
   Meanwhile, the embedding model (all-MiniLM-L6-v2) treats Karen Wickett's
   "information organization / metadata / knowledge representation" as semantically
   close to "information governance / privacy," so her focused, single-topic chunk
   won rank 1. (Note: 150-char overlap already prevented a true boundary split —
   the failure was ranking/dilution, not a cut phrase.)

**What you would change to fix it:**

Both fixes were applied:

1. **Added a dedicated `profile_madelyn_sanfilippo.txt`** assembled from the faculty
   directory, RMP reviews, and the Teachers-Ranked-Excellent recognition.
2. **Switched to section-aware structured chunking** (`chunk_documents_structured`
   in `ingest.py`): the directory is split one faculty entry per chunk, profiles are
   packed by section, and every chunk is prefixed with a `PROFESSOR: <name>` header
   so the name travels with its content.

After fix (section-aware chunking + Madelyn profile, top-5):

| rank | distance | source                         | chunk                          |
| ---- | -------- | ------------------------------ | ------------------------------ |
| 1    | 0.2272   | faculty_listing.txt            | 11 _(Madelyn entry — correct)_ |
| 2    | 0.2826   | profile_madelyn_sanfilippo.txt | 0 _(Madelyn — correct)_        |
| 3    | 0.4405   | faculty_listing.txt            | 15                             |
| 4    | 0.4724   | faculty_listing.txt            | 8                              |
| 5    | 0.4802   | profile_karen_wickett.txt      | 3                              |

Madelyn moved from rank 2 to **rank 1**, her best distance dropped from **0.508 to
0.227**, and the previously-winning Karen Wickett chunk fell to rank 5. Reproduce
with `python compare_chunking.py`.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the Chunking Strategy and
Retrieval Approach in `planning.md` first meant the implementation had concrete parameters to
target — chunk size 1000, overlap 150, `all-MiniLM-L6-v2`, top-k 5 — rather than guessing
during coding. The pipeline diagram also mapped cleanly onto modules (`ingest.py`,
`embed_retrieve.py`, `rag.py`), which kept each stage focused.

**One way your implementation diverged from the spec, and why:** The spec described
character-window chunking, but the implementation moved to section-aware structured chunking.
This came directly from a retrieval failure: the "governance / privacy" query ranked the wrong
professor first because blind windows diluted the faculty directory. Splitting the directory one
entry per chunk and prefixing chunks with the professor's name fixed the ranking (see Failure
Case Analysis), so the divergence was a deliberate, evidence-driven improvement over the
original plan.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- _What I gave the AI:_ The Retrieval Approach section of `planning.md` and the request to
  build the embedding + vector store + retrieval stage.
- _What it produced:_ `embed_retrieve.py` — embedding chunks with `all-MiniLM-L6-v2`, storing
  them in ChromaDB with source/position metadata, and a top-k cosine retrieval function.
- _What I changed or overrode:_ Set cosine distance with normalized embeddings and had the
  collection rebuild on each run to stay in sync with the corpus, rather than appending.

**Instance 2**

- _What I gave the AI:_ The failing retrieval output for the "governance / privacy" query
  (Karen Wickett ranked above Madelyn Sanfilippo) and asked it to diagnose and fix it.
- _What it produced:_ A diagnosis (data-coverage gap plus chunk dilution in the directory
  file), a new `profile_madelyn_sanfilippo.txt`, and section-aware structured chunking in
  `ingest.py`, plus `compare_chunking.py` to measure the before/after.
- _What I changed or overrode:_ Kept the original character-window chunker alongside the new
  one as a comparison baseline instead of deleting it, so the before/after numbers stay
  reproducible.
