from pathlib import Path
import json
import re


DOCUMENTS_DIR = Path("documents")
OUTPUT_FILE = Path("chunks.json")

CHUNK_SIZE = 700
CHUNK_OVERLAP = 150


def clean_text(text: str) -> str:
    """
    Clean extra spaces and blank lines.
    We are not changing the review wording, just cleaning spacing.
    """
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def get_document_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("Document Title:"):
            return line.replace("Document Title:", "").strip()
    return "Unknown document"


def get_professor_name(title: str) -> str:
    """
    Example title:
    Student reviews for Professor Nikola Baci
    """
    match = re.search(r"Professor\s+(.+)", title)
    if match:
        return match.group(1).strip()
    return "Unknown professor"


def normalize_course(course: str) -> str:
    """
    Make course labels consistent.
    Example:
    CS340 -> CSCI340
    CSCI 340 -> CSCI340
    """
    course = course.strip()

    if course.lower() == "not listed":
        return "Not listed"

    match = re.search(r"(?:CSCI|CS)\s*(\d{3})", course, re.IGNORECASE)
    if match:
        return f"CSCI{match.group(1)}"

    return course


def extract_course(review_text: str) -> str:
    match = re.search(r"Course:\s*(.+)", review_text)
    if match:
        return normalize_course(match.group(1))
    return "Not listed"


def extract_sentiment(review_text: str) -> str:
    match = re.search(r"Sentiment:\s*(.+)", review_text)
    if match:
        return match.group(1).strip()
    return "Unknown"


def split_long_text(text: str) -> list[str]:
    """
    If a review is longer than CHUNK_SIZE, split it with overlap.
    Most reviews will stay as one chunk.
    """
    if len(text) <= CHUNK_SIZE:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def split_by_reviews(text: str) -> list[str]:
    """
    Split a professor file into separate review blocks.
    """
    parts = re.split(r"(?=Review\s+\d+)", text)

    header = parts[0].strip()
    reviews = [p.strip() for p in parts[1:] if p.strip()]

    chunks = []

    for review in reviews:
        full_review = f"{header}\n\n{review}".strip()
        chunks.extend(split_long_text(full_review))

    return chunks


def load_and_chunk_documents() -> list[dict]:
    """
    Load every .txt file from the documents folder and turn it into chunks.
    Each chunk keeps metadata: source, title, professor, course, sentiment.
    """
    all_chunks = []

    txt_files = sorted(DOCUMENTS_DIR.glob("*.txt"))

    if not txt_files:
        raise FileNotFoundError("No .txt files found in the documents folder.")

    for file_path in txt_files:
        raw_text = file_path.read_text(encoding="utf-8")
        cleaned_text = clean_text(raw_text)

        title = get_document_title(cleaned_text)
        professor = get_professor_name(title)

        chunks = split_by_reviews(cleaned_text)

        for i, chunk_text in enumerate(chunks):
            course = extract_course(chunk_text)
            sentiment = extract_sentiment(chunk_text)

            all_chunks.append(
                {
                    "id": f"{file_path.stem}_chunk_{i}",
                    "source": file_path.name,
                    "title": title,
                    "professor": professor,
                    "course": course,
                    "sentiment": sentiment,
                    "chunk_index": i,
                    "text": chunk_text,
                }
            )

    return all_chunks


def main():
    chunks = load_and_chunk_documents()

    OUTPUT_FILE.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Loaded and chunked documents from: {DOCUMENTS_DIR}")
    print(f"Total chunks created: {len(chunks)}")
    print(f"Saved chunks to: {OUTPUT_FILE}")
    print("\n--- Sample chunks ---\n")

    for chunk in chunks[:5]:
        print(f"ID: {chunk['id']}")
        print(f"Source: {chunk['source']}")
        print(f"Professor: {chunk['professor']}")
        print(f"Course: {chunk['course']}")
        print(f"Sentiment: {chunk['sentiment']}")
        print(f"Title: {chunk['title']}")
        print("Text:")
        print(chunk["text"][:700])
        print("\n" + "-" * 80 + "\n")


if __name__ == "__main__":
    main()