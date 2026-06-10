# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

The domain I chose is student reviews of selected Information Management professors at the University of Illinois Urbana-Champaign. This domain provides insights into professors' teaching and grading styles, helping not only Information Management students but also students from other programs who are interested in taking IM courses make more informed course-selection decisions. This information is often difficult to find because it is scattered across the internet. By gathering relevant pages and passages from multiple sources, the system can generate more comprehensive insights and make the information easier to access.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| #   | Source                                            | Description                                                                                               | URL or location                                                                                  |
| --- | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| 1   | RMP – Jingrui He                                  | Student reviews of machine learning and data science courses taught by Jingrui He.                        | https://www.ratemyprofessors.com/professor/2766039                                               |
| 2   | RMP – Yoo-Seong Song                              | Student reviews of business consulting and industry-focused courses taught by Yoo-Seong Song.             | https://www.ratemyprofessors.com/professor/1861158                                               |
| 3   | RMP – Kevin Trainor                               | Student reviews of Python programming and information processing courses taught by Kevin Trainor.         | https://www.ratemyprofessors.com/professor/1861162                                               |
| 4   | RMP – John Weible                                 | Student reviews of IT management and leadership courses taught by John Weible.                            | https://www.ratemyprofessors.com/professor/1861164                                               |
| 5   | RMP – Karen Wickett                               | Student reviews of information organization and metadata-related courses taught by Karen Wickett.         | https://www.ratemyprofessors.com/professor/1861165                                               |
| 6   | RMP – Martin Wolske                               | Student reviews of community informatics and project-based courses taught by Martin Wolske.               | https://www.ratemyprofessors.com/professor/1861166                                               |
| 7   | RMP – Brandon Batzloff                            | Student reviews of introductory Information Management courses taught by Brandon Batzloff.                | https://www.ratemyprofessors.com/professor/2924903                                               |
| 8   | RMP – Madelyn Sanfilippo                          | Student reviews of information governance, privacy, and policy courses taught by Madelyn Sanfilippo       | https://www.ratemyprofessors.com/professor/2827901                                               |
| 9   | iSchool Faculty Profile – Jingrui He              | Official faculty profile including research interests, teaching areas, and academic background.           | https://ischool.illinois.edu/people/jingrui-he                                                   |
| 10  | iSchool Faculty Profile – Yoo-Seong Song          | Official faculty profile including industry experience, teaching activities, and professional background. | https://ischool.illinois.edu/people/yoo-seong-song                                               |
| 11  | iSchool Faculty Profile – Karen Wickett           | Official faculty profile describing research interests, teaching areas, and academic career.              | https://ischool.illinois.edu/people/karen-wickett                                                |
| 12  | iSchool Faculty Profile – David Charles           | Official faculty profile covering IT management expertise and teaching responsibilities.                  | https://ischool.illinois.edu/people/david-charles                                                |
| 13  | iSchool Faculty Profile – Renee Hendricks         | Official faculty profile covering health informatics, process mining, and research interests.             | https://ischool.illinois.edu/people/renee-hendricks                                              |
| 14  | iSchool Faculty Listing                           | Directory of faculty members, titles, and research areas within the School of Information Sciences.       | https://ischool.illinois.edu/people/faculty                                                      |
| 15  | iSchool – Teachers Ranked Excellent (Spring 2025) | Official recognition of instructors receiving outstanding teaching evaluations from students.             | https://ischool.illinois.edu/news-events/news/2025/09/record-number-instructors-ranked-excellent |

|

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 1000 characters

**Overlap:** 150 characters

**Reasoning:** Most of my documents are relatively short faculty profiles, review pages, and university news articles. I chose a chunk size of 1000 characters with a 150 characters overlap. A larger chunk size helps preserve context in documents that contain lists of faculty names or teaching awards, where splitting the text too aggressively could produce chunks containing only names without sufficient context. The overlap helps retain information that may appear near chunk boundaries.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** I am using the all-MiniLM-L6-v2 embedding model through Sentence Transformers because it provides a good balance between retrieval quality and efficiency for a relatively small corpus.

**Top-k:** I will use a top-k value of 5. Since information about a professor may be distributed across multiple sources, retrieving the top five most relevant chunks helps provide more complete context while still limiting irrelevant information.

**Production tradeoff reflection:** If I were deploying this system for real users and cost were not a constraint, I would consider using a larger and more accurate embedding model. The most important factors would be retrieval accuracy on educational and course-related content, as well as the ability to correctly associtate professors, courses, and student reviews. Multilingual support would be less important because the corpus primarily consists of English-language content related to a U.S. university. Latency would still be a consideration, but I would prioritize retrieval quality over speed.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question                                                                                                | Expected answer                                                                          |
| --- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 1   | Who should I look up if I am interested in machine learning courses in the IM program?                  | Jingrui He                                                                               |
| 2   | Who is the MSIM Program Director?                                                                       | Jingrui He                                                                               |
| 3   | Which professor has significant consulting and industry experience that is reflected in their teaching? | Yoo-Seong Song                                                                           |
| 4   | Which professors in the knowledge base were recognized as Teachers Ranked Excellent in Spring 2025?     | Jingrui He, Yoo-Seong Song, Kevin Trainor, John Weible, and Karen Wickett (among others) |
| 5   | Which professor specializes in information governance and privacy-related topics?                       | Madelyn Sanfilippo                                                                       |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Conflicting or inconsistent information across sources. Student reviews on RMP are subjective and may not always align with official faculty profiles. As as result, the system may retrieve information that presents different perspective on the same professor.
2. Important context may be split across chunk boundaries. Some documents contain lists of faculty names or award recipients, and if the chunk size is too small, a chunk may contain only names without the surrounding explanation. This could reduce retrieval quality and lead to incomplete answers.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```text
                    UIUC IM Professor Sources
       (RMP Reviews, Faculty Profiles, University News)
                                   │
                                   ▼
┌─────────────────────────────────────────────┐
│             Source Documents                │
│               (.txt files)                  │
└─────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────┐
│             Document Ingestion              │
│                (TextLoader)                 │
└─────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────┐
│                 Chunking                    │
│ chunk_size=1000, overlap=150                │
└─────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────┐
│         Embedding + Vector Store            │
│ all-MiniLM-L6-v2 + ChromaDB                 │
└─────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────┐
│                 Retrieval                   │
│ Similarity Search (top-k = 5)               │
└─────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────┐
│                Generation                   │
│ Groq                                        │
│ Answer + Source Attribution                 │
└─────────────────────────────────────────────┘
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

| Pipeline Stage           | AI Tool | Input Provided                                                            | Expected Output                                                         | Verification                                                                                                          |
| ------------------------ | ------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Document Ingestion       | Claude  | Source URLs and project requirements                                      | Python code that loads .txt documents from the data directory           | Verify that all text files are loaded correctly                                                                       |
| Chunking                 | Claude  | Chunking strategy (chunk size = 1000, overlap = 150) from planning.md     | A `chunk_text()` function                                               | Check several sample documents to ensure chunks respect the specified size and overlap while preserving context       |
| Embedding + Vector Store | Claude  | Embedding model choice (`all-MiniLM-L6-v2`) and vector store requirements | Code that generates embeddings and stores them in ChromaDB              | Confirm that all chunks are embedded and can be retrieved from the vector database                                    |
| Retrieval                | Claude  | Retrieval requirements (top-k = 5) and evaluation questions               | Retrieval code that performs similarity search against the vector store | Test each evaluation query and verify that relevant chunks appear among the retrieved results                         |
| Generation               | Claude  | Prompt template, retrieved chunks, and expected answer format             | RAG pipeline code that generates answers using retrieved context        | Compare generated answers against expected answers in the evaluation plan and verify that sources are cited correctly |
