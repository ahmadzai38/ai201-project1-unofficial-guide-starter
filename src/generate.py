import os
from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve


MODEL_NAME = "llama-3.3-70b-versatile"


def format_context(chunks: list[dict]) -> str:
    context_parts = []

    for i, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"""[Chunk {i}]
Source: {chunk['source']}
Professor: {chunk['professor']}
Course: {chunk['course']}
Sentiment: {chunk['sentiment']}

{chunk['text']}
"""
        )

    return "\n\n".join(context_parts)


def unique_sources(chunks: list[dict]) -> list[str]:
    sources = []

    for chunk in chunks:
        label = (
            f"{chunk['source']} "
            f"(Professor: {chunk['professor']}, "
            f"Course: {chunk['course']}, "
            f"Chunk: {chunk['chunk_index']})"
        )

        if label not in sources:
            sources.append(label)

    return sources


def ask(question: str) -> dict:
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Make sure your .env file is set up.")

    client = Groq(api_key=api_key)

    chunks = retrieve(question, top_k=4)
    context = format_context(chunks)

    system_prompt = """
You are a grounded RAG assistant for an unofficial guide to Queens College Computer Science professors.

Rules:
1. Answer using ONLY the provided context chunks.
2. Do not use outside knowledge.
3. If the context does not contain enough information, say: "I do not have enough information in the documents to answer that."
4. Be honest if reviews are mixed or contradictory.
5. Mention the source document names in the answer.
6. Keep the answer clear and useful for a student.
"""

    user_prompt = f"""
Question:
{question}

Retrieved context:
{context}

Answer:
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": unique_sources(chunks),
        "chunks": chunks,
    }


def main():
    question = "What do students say about Jackson Yeh's CSCI240 exams and project?"
    result = ask(question)

    print("\nQUESTION:")
    print(question)

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for source in result["sources"]:
        print(f"- {source}")


if __name__ == "__main__":
    main()