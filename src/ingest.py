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
    We are not changing the review wording, just making spacing cleaner.
    """
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def get_document_title(text: str) -> str:
    """
    Try to find the document title from the top of the file.
    """
    for line in text.splitlines():
        if line.startswith("Document Title:"):
            return line.replace("Document Title:", "").strip()
    return "Unknown document"


def split_by_reviews(text: str) -> list[str]:
    """
    Split a professor file into separate review blocks.

    Example:
    Review 1 ... Review 2 ... Review 3 ...

    This is better than blindly cutting every 700 characters because
    each review already has a natural structure.
    """
    parts = re.split(r"(?=Review\s+\d+)", text)

    header = parts[0].strip()
    reviews = [p.strip() for p in parts[1:] if p.strip()]

    chunks = []
    for review in reviews:
        full_review = f"{header}\n\n{review}".strip()
        chunks.extend(split_long_text(full_review))

    return chunks


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


def load_and_chunk_documents() -> list[dict]:
    """
    Load every .txt file from the documents folder and turn it into chunks.
    Each chunk keeps metadata about where it came from.
    """
    all_chunks = []

    txt_files = sorted(DOCUMENTS_DIR.glob("*.txt"))

    if not txt_files:
        raise FileNotFoundError("No .txt files found in the documents folder.")

    for file_path in txt_files:
        raw_text = file_path.read_text(encoding="utf-8")
        cleaned_text = clean_text(raw_text)
        title = get_document_title(cleaned_text)

        chunks = split_by_reviews(cleaned_text)

        for i, chunk_text in enumerate(chunks):
            all_chunks.append(
                {
                    "id": f"{file_path.stem}_chunk_{i}",
                    "source": file_path.name,
                    "title": title,
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
        print(f"Title: {chunk['title']}")
        print("Text:")
        print(chunk["text"][:700])
        print("\n" + "-" * 80 + "\n")


if __name__ == "__main__":
    main()