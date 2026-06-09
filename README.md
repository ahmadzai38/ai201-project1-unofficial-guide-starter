# The Unofficial Guide — Project 1

## Demo Video

Demo video: [Watch here]PASTE_https://drive.google.com/file/d/1FbefAc0XwE7aK4p0QIYXVC_wkiCWN04L/view?usp=sharingYOUR_DEMO_LINK_HERE

## Domain

My system covers unofficial student reviews of Queens College Computer Science professors and courses. This knowledge is valuable because official college pages usually only show course descriptions, prerequisites, and credits. They do not explain what students actually experience in the class, such as teaching style, exam difficulty, workload, grading, self-study expectations, or whether a professor is beginner-friendly.

This information is hard to find through official channels because students usually share it in informal places like Rate My Professor, Reddit, Discord, or conversations with other students. My RAG system helps organize this unofficial information and answer questions using the collected review documents.


---

## Document Sources

| #  | Source            | Type                     | URL or file path                        |
| -- | ----------------- | ------------------------ | --------------------------------------- |
| 1  | Rate My Professor | Student review text file | `documents/rmp_anne_smith_thompson.txt` |
| 2  | Rate My Professor | Student review text file | `documents/rmp_bojana_obrenic.txt`      |
| 3  | Rate My Professor | Student review text file | `documents/rmp_nikola_baci.txt`         |
| 4  | Rate My Professor | Student review text file | `documents/rmp_xinying_chyn.txt`        |
| 5  | Rate My Professor | Student review text file | `documents/rmp_jackson_yeh.txt`         |
| 6  | Rate My Professor | Student review text file | `documents/rmp_simina_fluture.txt`      |
| 7  | Rate My Professor | Student review text file | `documents/rmp_alex_ryba.txt`           |
| 8  | Rate My Professor | Student review text file | `documents/rmp_kenneth_lord.txt`        |
| 9  | Rate My Professor | Student review text file | `documents/rmp_jerry_waxman.txt`        |
| 10 | Rate My Professor | Student review text file | `documents/rmp_md_mahbubur_rahman.txt`  |

Each document contains student reviews for one Queens College Computer Science professor. The documents cover different courses such as CSCI111, CSCI211, CSCI212, CSCI240, CSCI313, CSCI320, CSCI323, CSCI331, CSCI340, CSCI343, CSCI344, CSCI355, and CSCI381.


---
## How to Run

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:

```powershell
Copy-Item .env.example .env
```

4. Open the `.env` file and replace the placeholder with a real Groq API key:

```text
GROQ_API_KEY=your_key_here
```

5. Build the chunks:

```powershell
python src/ingest.py
```

6. Build the vector store and test retrieval:

```powershell
python src/retrieve.py
```

7. Run the Gradio app:

```powershell
python app.py
```

8. Open the local Gradio link in the browser. It is usually:

```text
http://127.0.0.1:7860
```

Note: The `.env` file should not be committed to GitHub because it contains the Groq API key.





## Chunking Strategy

Chunk size:
Review-based chunking. Each review usually becomes one chunk.

Overlap:
150 characters only if a review is longer than about 700 characters.

Why these choices fit your documents:
My documents are made of short student reviews, not long textbook chapters or long FAQ pages. Each review already contains a complete student opinion with course, sentiment, and review text. Because of this, review-based chunking works better than blindly splitting every 700 characters.

If a review is longer than about 700 characters, the code splits it into smaller chunks with 150 characters of overlap. The overlap helps keep important context together if the review is split near information about exams, grading, workload, or teaching style.

Before chunking, the code cleans extra spacing and blank lines but does not rewrite the student reviews.

Final chunk count:
100 chunks

---

## Embedding Model

Model used:
all-MiniLM-L6-v2 from sentence-transformers

Production tradeoff reflection:
I used all-MiniLM-L6-v2 because it is free, runs locally, and is good enough for a small project with 100 student review chunks. It is also fast enough to use during local development.

If I were deploying this system for real users and cost was not a constraint, I would compare other embedding models based on accuracy, latency, cost, context length, and how well they handle informal student language. I would also consider multilingual support because student comments can sometimes include slang, abbreviations, or non-standard grammar. For a larger system, I might use a stronger API-hosted embedding model or add a reranking step to improve results for broad comparison questions.


---

## Grounded Generation

System prompt grounding instruction:
My system uses a prompt that tells the model to answer only from the retrieved context chunks. The prompt includes these rules:

You are a grounded RAG assistant for an unofficial guide to Queens College Computer Science professors.

Rules:
1. Answer using ONLY the provided context chunks.
2. Do not use outside knowledge.
3. If the context does not contain enough information, say: "I do not have enough information in the documents to answer that."
4. Be honest if reviews are mixed or contradictory.
5. Mention the source document names in the answer.
6. Keep the answer clear and useful for a student.

The retrieved chunks are formatted with metadata before they are sent to the LLM. Each chunk includes the source file, professor name, course, sentiment, and review text. This helps the model understand where the information came from.

The retrieval system also uses metadata filtering. If a question mentions a professor and course, such as “Nikola Baci’s CSCI313,” the system filters results to that professor and course before generation. This helps prevent unrelated chunks from being used.

How source attribution is surfaced in the response:
The Gradio interface shows the generated answer and a separate sources section. The sources include the file name, professor, course, and chunk number. For example:

- rmp_jackson_yeh.txt (Professor: Jackson Yeh, Course: CSCI240, Chunk: 2)

This makes it clear which document chunks were used to generate the answer.


---
## Sample Chunks

Here are five sample chunks created by the ingestion pipeline. Each chunk keeps the source document, professor, course, sentiment, and review text together.

### Sample Chunk 1

**Source:** `rmp_alex_ryba.txt`
**Professor:** Alex Ryba
**Course:** CSCI212
**Sentiment:** Mixed
**Chunk summary:** The review says the lectures were heavy but informative, the exams contained syntax, and students should practice coding outside class and not skip lab.

### Sample Chunk 2

**Source:** `rmp_jackson_yeh.txt`
**Professor:** Jackson Yeh
**Course:** CSCI240
**Sentiment:** Positive
**Chunk summary:** The review says CSCI240 has quizzes, a midterm, a final, and a Logisim project. It also says the exams are open-book and that Professor Yeh gives straightforward examples.

### Sample Chunk 3

**Source:** `rmp_bojana_obrenic.txt`
**Professor:** Bojana Obrenic
**Course:** CSCI320
**Sentiment:** Positive
**Chunk summary:** The review says students should practice questions from her problem book, attend lectures, and use the problem book to understand what exams look like.

### Sample Chunk 4

**Source:** `rmp_nikola_baci.txt`
**Professor:** Nikola Baci
**Course:** CSCI313
**Sentiment:** Positive
**Chunk summary:** The review says Baci explains data structures clearly, takes time to answer questions, gives fair exams, and includes LeetCode-style problems.

### Sample Chunk 5

**Source:** `rmp_kenneth_lord.txt`
**Professor:** Kenneth Lord
**Course:** CSCI212
**Sentiment:** Negative
**Chunk summary:** The review says students should be prepared to self-study because the lectures mostly read from slides and the class has several projects.

---

## Retrieval Test Results

I tested retrieval before generation to check whether the system returned relevant chunks.

### Retrieval Test 1

**Query:** What do students say about Jackson Yeh’s CSCI240 exams and project?

**Top returned chunks:**

1. `rmp_jackson_yeh.txt`, Chunk 2 — mentions online exams/quizzes and the Logisim project.
2. `rmp_jackson_yeh.txt`, Chunk 7 — mentions 2 exams, 2 quizzes, and a project.
3. `rmp_jackson_yeh.txt`, Chunk 8 — mentions fair exams and recorded lectures.
4. `rmp_jackson_yeh.txt`, Chunk 0 — mentions open-book exams, quizzes, midterm/final, and the Logisim project.

**Why the chunks are relevant:**
All four chunks are from Jackson Yeh’s CSCI240 reviews and directly mention exams, quizzes, or the Logisim project.

### Retrieval Test 2

**Query:** What advice do students give for passing Bojana Obrenic’s CSCI320?

**Top returned chunks:**

1. `rmp_bojana_obrenic.txt`, Chunk 0 — mentions using the problem book and going to lectures.
2. `rmp_bojana_obrenic.txt`, Chunk 2 — mentions midterm/final structure and passing requirements.
3. `rmp_bojana_obrenic.txt`, Chunk 7 — mentions grading criteria, Clint videos, and exam preparation.
4. `rmp_bojana_obrenic.txt`, Chunk 1 — mentions going to class, participating, review materials, and extra credit.

**Why the chunks are relevant:**
All returned chunks are from Bojana Obrenic’s CSCI320 reviews and include advice about passing, studying, exams, and outside resources.

### Retrieval Test 3

**Query:** What do students say about Nikola Baci’s CSCI313?

**Top returned chunks:**

1. `rmp_nikola_baci.txt`, Chunk 1 — mentions Data Structures, fair exams, LeetCode, and studying.
2. `rmp_nikola_baci.txt`, Chunk 2 — mentions clear slides, in-class demos, and exam structure.
3. `rmp_nikola_baci.txt`, Chunk 3 — mentions that he explains well but students need to practice and study.
4. `rmp_nikola_baci.txt`, Chunk 0 — mentions self-study, Java preparation, surprise quizzes, and exams.

**Why the chunks are relevant:**
All returned chunks are from Nikola Baci’s CSCI313 reviews and directly describe the course, teaching style, exams, and preparation advice.

---

## Example Responses

### Example Response 1

**Query:** What do students say about Professor Jackson Yeh’s CSCI240 exams and project?

**System response summary:**
The system said students describe the exams as fair or not too difficult. It mentioned open-book exams, quizzes, the midterm/final, and the Logisim project. It also said the project can be the hardest part but is manageable.

**Sources shown:**

* `rmp_jackson_yeh.txt` (Professor: Jackson Yeh, Course: CSCI240, Chunk: 7)
* `rmp_jackson_yeh.txt` (Professor: Jackson Yeh, Course: CSCI240, Chunk: 2)
* `rmp_jackson_yeh.txt` (Professor: Jackson Yeh, Course: CSCI240, Chunk: 8)
* `rmp_jackson_yeh.txt` (Professor: Jackson Yeh, Course: CSCI240, Chunk: 0)

### Example Response 2

**Query:** What advice do students give for passing Professor Bojana Obrenic’s CSCI320?

**System response summary:**
The system said students recommend practicing from the problem book, attending lectures, reviewing materials, using outside resources, and paying attention to exams and the grading curve.

**Sources shown:**

* `rmp_bojana_obrenic.txt` (Professor: Bojana Obrenic, Course: CSCI320, Chunk: 0)
* `rmp_bojana_obrenic.txt` (Professor: Bojana Obrenic, Course: CSCI320, Chunk: 2)
* `rmp_bojana_obrenic.txt` (Professor: Bojana Obrenic, Course: CSCI320, Chunk: 7)
* `rmp_bojana_obrenic.txt` (Professor: Bojana Obrenic, Course: CSCI320, Chunk: 1)

### Out-of-Scope Refusal

**Query:** What do the documents say about campus dining at Queens College?

**System response summary:**
The system correctly said it did not have enough information in the documents to answer. It explained that the documents are about Computer Science professor reviews, not campus dining.

---

## Query Interface

The query interface is a Gradio web app. The user types a question into a textbox and clicks the Ask button. The app returns two outputs: a grounded answer and a list of source chunks used to generate the answer.

### Sample Interaction Transcript

**User:** What do students say about Professor Jackson Yeh’s CSCI240 exams and project?

**System:** Students describe the exams as fair or not too difficult. The answer mentions open-book exams, quizzes, the midterm/final, and the Logisim project. It also notes that the project can be the hardest part but is manageable.

**Sources:**

* `rmp_jackson_yeh.txt` (Professor: Jackson Yeh, Course: CSCI240, Chunk: 7)
* `rmp_jackson_yeh.txt` (Professor: Jackson Yeh, Course: CSCI240, Chunk: 2)
* `rmp_jackson_yeh.txt` (Professor: Jackson Yeh, Course: CSCI240, Chunk: 8)
* `rmp_jackson_yeh.txt` (Professor: Jackson Yeh, Course: CSCI240, Chunk: 0)





## Evaluation Report


I tested the system with five questions from my `planning.md`. For each question, I checked the expected answer, the system response, retrieval quality, and response accuracy.

### 1. What do students say about Professor Jackson Yeh’s CSCI240 exams and project?

**Expected answer:**
Students should mention quizzes, a midterm, a final, open-book or online exams, and the Logisim/circuit project.

**System response summarized:**
The system said students describe the exams as fair or not too difficult. It mentioned open-book exams, quizzes, the midterm/final, and the Logisim project. It also said the project can be the hardest part but is manageable.

**Retrieval quality:** Relevant
**Response accuracy:** Accurate

---

### 2. What advice do students give for passing Professor Bojana Obrenic’s CSCI320?

**Expected answer:**
Students should mention the problem book, going to class, studying exam-style questions, the grading curve, extra credit, and outside resources.

**System response summarized:**
The system said students recommend practicing from the problem book, attending lectures, reviewing materials, using outside resources, and paying attention to exams and the grading curve.

**Retrieval quality:** Relevant
**Response accuracy:** Accurate

---

### 3. What do students say about Professor Nikola Baci’s CSCI313?

**Expected answer:**
Students should mention that he explains clearly, but the class requires Java knowledge, LeetCode/homework practice, and self-study.

**System response summarized:**
The system said students generally describe him positively. It mentioned clear explanations, slides, demos, fair exams, LeetCode homework, Java preparation, and self-study.

**Retrieval quality:** Relevant
**Response accuracy:** Accurate

---

### 4. Which professors are described as requiring a lot of self-study or outside resources?

**Expected answer:**
The answer should mention professors whose reviews discuss self-study, online resources, textbooks, YouTube, problem books, or outside videos.

**System response summarized:**
The system mentioned Nikola Baci and Kenneth Lord. This was relevant, but it missed other possible professors from the documents, such as Anne Smith-Thompson, Simina Fluture, Jerry Waxman, or Md Mahbubur Rahman.

**Retrieval quality:** Partially relevant
**Response accuracy:** Partially accurate

---

### 5. What do the documents say about campus dining at Queens College?

**Expected answer:**
The system should say it does not have enough information because the documents are about Computer Science professor reviews, not campus dining.

**System response summarized:**
The system correctly said it did not have enough information in the documents to answer. It explained that the retrieved documents were about Computer Science professor reviews.

**Retrieval quality:** Relevant
**Response accuracy:** Accurate

**Retrieval quality labels:**  Relevant / Partially relevant / Off-target


**Response accuracy labels:**  Accurate / Partially accurate / Inaccurate


---

## Failure Case Analysis

**Question that failed:**
Which professors are described as requiring a lot of self-study or outside resources?

**What the system returned:**
The system returned an answer mentioning Nikola Baci and Kenneth Lord. These were relevant, but the answer was incomplete because other professors in the documents also had reviews that mentioned self-study, outside resources, textbooks, online resources, or learning independently.

**Root cause (tied to a specific pipeline stage):**
The issue happened mainly in the retrieval stage. The question was broad and asked for a comparison across many professors. Since the retriever only returns the top 4 chunks, it found some relevant chunks but did not retrieve every professor who matched the theme. This is not exactly a generation failure because the model answered based on the chunks it received. The bigger issue is that the retriever did not gather enough broad evidence across the whole corpus.

**What you would change to fix it:**
For broad comparison questions, I would increase top_k from 4 to a higher number, such as 8 or 12. I could also detect broad questions and retrieve more chunks automatically. Another improvement would be grouping retrieved chunks by professor before sending them to the LLM, so the answer covers more perspectives instead of focusing only on the top few matches. I could also add keyword expansion for terms like “self-study,” “outside resources,” “YouTube,” “textbook,” “online resources,” and “problem book.”

---

## Spec Reflection

**One way the spec helped you during implementation:**
The planning document helped me stay organized before writing code. It made me decide the domain, source documents, chunking strategy, embedding model, retrieval approach, and evaluation questions early. This made the coding process easier because I already knew what each pipeline stage needed to do.

The spec also helped me catch a mismatch between my original plan and actual implementation. I originally planned to chunk by character size, but after looking at the review format, review-based chunking made more sense. Updating the plan helped make the project more consistent.

**One way your implementation diverged from the spec, and why:**
My original chunking plan said I would use chunks of about 700 characters with 150 characters of overlap. During implementation, I changed this to review-based chunking because each review already contained a full student opinion. This worked better because it kept course, sentiment, and review text together.

I still kept the 700-character size and 150-character overlap as a fallback for long reviews. So the implementation did not completely abandon the original idea, but it adapted it to fit the structure of the documents better.

---

## AI Usage

**Instance 1**

What I gave the AI:
I gave ChatGPT my project idea, which was an unofficial guide to Queens College Computer Science professors and courses, and I shared examples of the Rate My Professor review documents.
What it produced:
ChatGPT helped me organize the documents into a consistent format with source, document title, school, department, URL, review number, course, sentiment, and review text. It also helped me decide to use one professor per document and to include a variety of positive, negative, and mixed reviews.
What I changed or overrode:
I made sure the review text stayed in the students’ original wording instead of being paraphrased. I also corrected course labels when needed, such as changing reviews that mentioned CSCI240 so they were not incorrectly labeled as CSCI313.

**Instance 2**

What I gave the AI:
I gave ChatGPT my planning.md sections, my chunking strategy, my document format, and the milestone requirements for building a RAG pipeline.
What it produced:
ChatGPT helped generate Python code for document ingestion, review-based chunking, embeddings with all-MiniLM-L6-v2, ChromaDB retrieval, Groq-based grounded generation, and a Gradio interface.
What I changed or overrode:
I tested the code at each milestone and adjusted it based on the results. For example, when retrieval returned a CSCI240 review for a CSCI313 question, I updated the pipeline to extract professor, course, and sentiment metadata and added metadata filtering. I also updated the retrieval code to use cosine similarity and normalized embeddings.