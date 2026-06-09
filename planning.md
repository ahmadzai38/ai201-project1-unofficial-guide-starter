# Project 1 Planning: The Unofficial Guide

Write this document before you write any pipeline code.
Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
Update this file before starting any stretch features.

---

## Domain

My domain is unofficial student reviews of Queens College Computer Science professors and courses. This knowledge is valuable because official college pages show course descriptions, but they do not tell students what the class feels like, how professors teach, how exams are structured, how much self-study is needed, or what advice other students give.

This guide is meant to help students ask plain-English questions like “Which professor is good for CSCI240?”, “Which classes require a lot of self-study?”, or “What do students say about exams?” and get answers based only on student review documents.
---

## Documents

My documents are 10 manually collected text files from Rate My Professor. Each document focuses on one Queens College Computer Science professor and includes multiple student reviews. I saved the reviews locally as .txt files so the RAG system uses my documents instead of doing a live web search.

#	Source	Description	URL or location
1	Rate My Professor	Student reviews for Professor Anne Smith-Thompson	documents/rmp_anne_smith_thompson.txt
2	Rate My Professor	Student reviews for Professor Bojana Obrenic	documents/rmp_bojana_obrenic.txt
3	Rate My Professor	Student reviews for Professor Nikola Baci	documents/rmp_nikola_baci.txt
4	Rate My Professor	Student reviews for Professor Xinying Chyn	documents/rmp_xinying_chyn.txt
5	Rate My Professor	Student reviews for Professor Jackson Yeh	documents/rmp_jackson_yeh.txt
6	Rate My Professor	Student reviews for Professor Simina Fluture	documents/rmp_simina_fluture.txt
7	Rate My Professor	Student reviews for Professor Alex Ryba	documents/rmp_alex_ryba.txt
8	Rate My Professor	Student reviews for Professor Kenneth Lord	documents/rmp_kenneth_lord.txt
9	Rate My Professor	Student reviews for Professor Jerry Waxman	documents/rmp_jerry_waxman.txt
10	Rate My Professor	Student reviews for Professor Md Mahbubur Rahman	documents/rmp_md_mahbubur_rahman.txt

The documents cover different courses such as CSCI111, CSCI211, CSCI212, CSCI240, CSCI313, CSCI320, CSCI323, CSCI331, CSCI340, CSCI343, CSCI344, CSCI355, and CSCI381. This variety should help the system answer questions about exams, grading, lectures, self-study, projects, homework, and professor teaching styles.

---

## Chunking Strategy

Chunk size: About 700 characters

Overlap: About 150 characters



Reasoning:

My documents are student reviews, so I will use review-based chunking. Each review will usually become one chunk because each review already contains a complete student opinion with course, sentiment, and review text. If a review is longer than about 700 characters, I will split it into smaller chunks with about 150 characters of overlap. This keeps chunks readable and self-contained while preventing very long reviews from mixing too many ideas.

The overlap helps if important information about exams, grading, or teaching style appears near the boundary between two chunks. If the chunks are too small, the system may retrieve fragments that do not fully explain the review. If the chunks are too large, the system may mix unrelated reviews about different courses or professors.

Since each review already has labels like professor name, course, sentiment, and review text, the chunks should stay easy to understand and cite.

---

## Retrieval Approach

Embedding model: all-MiniLM-L6-v2 from sentence-transformers

Vector store: ChromaDB

Top-k: 4 chunks per query

Production tradeoff reflection:

I will use all-MiniLM-L6-v2 because it runs locally, is free to use, and is good enough for a small student review project. It does not require API credits, which makes it practical for this assignment.

For each user question, I will retrieve the top 4 most relevant chunks. Retrieving too few chunks could miss important context. Retrieving too many chunks could add unrelated professor reviews and make the generated answer less focused.

If this were a real production system, I would compare embedding models based on accuracy, speed, cost, context length, and how well they understand informal student language. I would also consider whether the model works well with multilingual text, since students may write informally or use different language patterns.




---

## Evaluation Plan

#	Question	Expected answer
1	What do students say about Professor Jackson Yeh’s CSCI240 exams and project?	Students say his CSCI240 class usually includes quizzes, a midterm, a final, and a Logisim or circuit project. Many reviews mention open-note or online exams, recorded lectures, and a manageable project.
2	What advice do students give for passing Professor Bojana Obrenic’s CSCI320?	Students recommend going to class, using her problem book, studying exam-style questions, paying attention to the grading curve, and taking advantage of extra credit or generous grading.
3	What do students say about Professor Nikola Baci’s CSCI313?	Students say he explains data structures clearly, but the class requires self-study, Java knowledge, LeetCode or homework practice, and serious preparation.
4	Which professors are described as requiring a lot of self-study or outside resources?	The system should mention professors such as Nikola Baci, Anne Smith-Thompson, Simina Fluture, Jerry Waxman, Kenneth Lord, or Md Mahbubur Rahman depending on the retrieved chunks. The answer should explain which reviews mention self-study, outside videos, textbooks, problem books, or online resources.
5	What do the documents say about campus dining at Queens College?	The system should say it does not have enough information because the documents are about Computer Science professor reviews, not campus dining.
---

## Anticipated Challenges

The reviews are informal, emotional, and sometimes contradictory. One student may say a professor is helpful, while another student may say the same professor is confusing or hard to reach. The system needs to summarize both sides instead of pretending there is only one opinion.
Some reviews mention multiple topics in one paragraph, such as exams, grading, lectures, projects, and professor attitude. If the chunking is not done carefully, the system may retrieve only part of the useful context.
Some course labels may be inconsistent, such as “CS340” versus “CSCI340” or “343” versus “CSCI343.” I tried to make the course names consistent in the documents, but retrieval may still be affected if wording is different across reviews.
The system must include source attribution. If the answer does not show which document the information came from, it will not be fully grounded.
The model may try to answer from general knowledge if the retrieved chunks do not contain enough information. To avoid this, the generation prompt must clearly say to answer only from the provided context and to say “I do not have enough information” when the documents do not answer the question.

## Architecture

Raw Documents
10 .txt files in documents/
        ↓
Document Ingestion
Python loads each .txt file and stores source filename metadata
        ↓
Cleaning
Normalize spacing and remove empty text
        ↓
Chunking
Split text into ~700 character chunks with ~150 character overlap
        ↓
Embedding
Use sentence-transformers all-MiniLM-L6-v2
        ↓
Vector Store
Store chunk embeddings and metadata in ChromaDB
        ↓
Retrieval
Given a user question, retrieve top 4 most relevant chunks
        ↓
Generation
Use Groq LLM to answer only from retrieved chunks
        ↓
Final Output
Show grounded answer + source document names

Tools/libraries:

Document loading: Python file reading
Chunking: Custom Python function
Embeddings: sentence-transformers with all-MiniLM-L6-v2
Vector store: ChromaDB
LLM: Groq with llama-3.3-70b-versatile
Interface: Gradio web app

---

## AI Tool Plan

I will use ChatGPT and/or Claude to help me implement and debug the project, but I will guide the AI with my own project plan and review the output.

For the ingestion and chunking step, I will give the AI my Documents section and Chunking Strategy section. I will ask it to write Python code that loads all .txt files from the documents/ folder, cleans the text, attaches source metadata, and splits the text into chunks of about 700 characters with 150 characters of overlap. I will verify the output by printing at least 5 chunks and checking that they are readable and connected to the correct source file.

For the embedding and retrieval step, I will give the AI my Retrieval Approach section and Architecture section. I will ask it to write code using sentence-transformers and ChromaDB to embed the chunks, store them with metadata, and retrieve the top 4 chunks for a query. I will verify this by testing at least 3 evaluation questions and checking whether the retrieved chunks actually relate to the question.

For the generation step, I will ask the AI to help write a prompt that forces the LLM to answer only using the retrieved context. The prompt should tell the model to say it does not have enough information if the documents do not answer the question. I will verify this by asking an out-of-scope question about campus dining and checking that the system refuses to invent an answer.

For the interface step, I will ask the AI to help build a simple Gradio app with one input box for the user question and output areas for the answer and sources. I will verify it by running the app locally and testing several questions.

For the README and evaluation report, I will use AI to help organize my writing, but I will base the results on my actual system outputs. I will include both successful examples and at least one failure case.

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
