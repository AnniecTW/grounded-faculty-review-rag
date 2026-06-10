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

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question | Expected answer |
| --- | -------- | --------------- |
| 1   |          |                 |
| 2   |          |                 |
| 3   |          |                 |
| 4   |          |                 |
| 5   |          |                 |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
