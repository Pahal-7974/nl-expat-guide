"""
ingest.py

Reads every .txt file in source_docs/, splits each into overlapping chunks,
embeds the chunks with a local sentence-transformers model, and builds a
FAISS index for fast similarity search at query time.

Run this once (or whenever source_docs/ changes):
    python src/ingest.py

Outputs:
    index/faiss.index   - the vector index
    index/chunks.pkl    - the chunk text + metadata, aligned by row to the index
"""

import os
import re
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

SOURCE_DIR = os.path.join(os.path.dirname(__file__), "..", "source_docs")
INDEX_DIR = os.path.join(os.path.dirname(__file__), "..", "index")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # small, fast, free, runs locally

# Tradeoff: smaller chunks -> more precise retrieval but less surrounding context.
# Larger chunks -> more context per chunk but retrieval gets noisier (a chunk
# might only be partially relevant to the query). Currently 1 document -> 1 chunk.
CHUNK_SIZE_WORDS = 350
CHUNK_OVERLAP_WORDS = 50


def parse_doc(filepath):
    """Extract metadata header (TITLE, SOURCE_URL, ...) and body text from a source doc."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    metadata = {}
    body_start = 0
    for i, line in enumerate(lines):
        match = re.match(r"^([A-Z_0-9]+):\s*(.*)$", line)
        if match:
            metadata[match.group(1)] = match.group(2)
            body_start = i + 1
        elif line.strip() == "" and metadata:
            body_start = i + 1
            break

    body = "\n".join(lines[body_start:]).strip()
    return metadata, body


def chunk_text(text, chunk_size=CHUNK_SIZE_WORDS, overlap=CHUNK_OVERLAP_WORDS):
    """Simple word-count based sliding-window chunker."""
    words = text.split()
    if len(words) <= chunk_size: # Current code returns here, but below loop is for potential future use with bigger documents and provides scalability.
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap
    return chunks


def build_index():
    if not os.path.isdir(SOURCE_DIR):
        raise FileNotFoundError(f"No source_docs directory at {SOURCE_DIR}")

    os.makedirs(INDEX_DIR, exist_ok=True) # exist_ok prevents runtime fs crash

    print(f"Loading embedding model ({EMBEDDING_MODEL})...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    all_chunks = []  # list of dicts: {text, title, source_url, source_url_2}

    filenames = f for f in os.listdir(SOURCE_DIR) if f.endswith(".txt")
    print(f"Found {len(filenames)} source documents.")

    for filename in filenames:
        filepath = os.path.join(SOURCE_DIR, filename)
        metadata, body = parse_doc(filepath)
        title = metadata.get("TITLE", filename)
        source_url = metadata.get("SOURCE_URL", "")
        source_url_2 = metadata.get("SOURCE_URL_2", "")

        for chunk in chunk_text(body):
            all_chunks.append({
                "text": chunk,
                "title": title,
                "source_url": source_url,
                "source_url_2": source_url_2,
                "filename": filename,
            })

    print(f"Created {len(all_chunks)} chunks. Embedding...")
    texts = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # Normalise so that inner product == cosine similarity.
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # exact search; fine for upto ~1M vectors.
    index.add(embeddings)

    faiss.write_index(index, os.path.join(INDEX_DIR, "faiss.index"))
    with open(os.path.join(INDEX_DIR, "chunks.pkl"), "wb") as f:
        pickle.dump(all_chunks, f)

    print(f"Done. Index has {index.ntotal} vectors, dimension {dim}.")


if __name__ == "__main__":
    build_index()
