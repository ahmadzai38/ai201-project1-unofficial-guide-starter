from pathlib import Path
import json
import re

import chromadb
from sentence_transformers import SentenceTransformer


CHUNKS_FILE = Path("chunks.json")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "professor_reviews"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 4


def load_chunks():
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            "chunks.json not found. Run: python src/ingest.py first."
        )

    with CHUNKS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def detect_course(query: str) -> str | None:
    """
    Detect course from user query.
    Example:
    CSCI313 -> CSCI313
    CS 240 -> CSCI240
    """
    match = re.search(r"\b(?:CSCI|CS)\s*(\d{3})\b", query, re.IGNORECASE)
    if match:
        return f"CSCI{match.group(1)}"
    return None


def detect_professor(query: str, known_professors: list[str]) -> str | None:
    """
    Detect professor name from user query by checking names in metadata.
    Example:
    query contains "Nikola Baci" -> Nikola Baci
    """
    query_lower = query.lower()

    for professor in known_professors:
        if professor.lower() in query_lower:
            return professor

    return None


def build_where_filter(query: str, chunks: list[dict]):
    """
    Build Chroma metadata filter based on professor and course.
    """
    course = detect_course(query)

    known_professors = sorted(
        set(chunk["professor"] for chunk in chunks if chunk["professor"] != "Unknown professor")
    )
    professor = detect_professor(query, known_professors)

    filters = []

    if course:
        filters.append({"course": course})

    if professor:
        filters.append({"professor": professor})

    if len(filters) == 0:
        return None

    if len(filters) == 1:
        return filters[0]

    return {"$and": filters}


def build_vector_store():
    """
    Embed all chunks and store them in ChromaDB.
    """
    chunks = load_chunks()

    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    texts = [chunk["text"] for chunk in chunks]
    ids = [chunk["id"] for chunk in chunks]

    metadatas = [
        {
            "source": chunk["source"],
            "title": chunk["title"],
            "professor": chunk["professor"],
            "course": chunk["course"],
            "sentiment": chunk["sentiment"],
            "chunk_index": chunk["chunk_index"],
        }
        for chunk in chunks
    ]

    print("Creating embeddings...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    ).tolist()

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Delete old collection so reruns use fresh metadata.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Saved {len(chunks)} chunks to ChromaDB collection: {COLLECTION_NAME}")


def retrieve(query: str, top_k: int = TOP_K):
    """
    Retrieve top relevant chunks for a user query.
    Uses metadata filtering when the query includes a professor name or course.
    """
    chunks = load_chunks()
    where_filter = build_where_filter(query, chunks)

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    ).tolist()

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)

    query_args = {
        "query_embeddings": query_embedding,
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }

    if where_filter:
        query_args["where"] = where_filter
        print(f"Using metadata filter: {where_filter}")

    results = collection.query(**query_args)

    retrieved = []

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append(
            {
                "text": document,
                "source": metadata["source"],
                "title": metadata["title"],
                "professor": metadata["professor"],
                "course": metadata["course"],
                "sentiment": metadata["sentiment"],
                "chunk_index": metadata["chunk_index"],
                "distance": distance,
            }
        )

    return retrieved


def test_retrieval():
    test_queries = [
        "What do students say about Jackson Yeh's CSCI240 exams and project?",
        "What advice do students give for passing Bojana Obrenic's CSCI320?",
        "What do students say about Nikola Baci's CSCI313?",
    ]

    for query in test_queries:
        print("\n" + "=" * 100)
        print(f"QUERY: {query}")
        print("=" * 100)

        results = retrieve(query)

        for i, result in enumerate(results, start=1):
            print(f"\nResult {i}")
            print(f"Source: {result['source']}")
            print(f"Professor: {result['professor']}")
            print(f"Course: {result['course']}")
            print(f"Sentiment: {result['sentiment']}")
            print(f"Chunk index: {result['chunk_index']}")
            print(f"Distance: {result['distance']:.4f}")
            print("Text:")
            print(result["text"][:900])
            print("-" * 100)


def main():
    build_vector_store()
    test_retrieval()


if __name__ == "__main__":
    main()