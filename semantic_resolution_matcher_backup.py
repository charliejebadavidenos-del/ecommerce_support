
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from storage import load_approved_resolutions
from test_delivery_safety import safe_delivery_match


_model = None


def get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


def match_semantic_resolutions(
    ticket_text,
    limit=3,
    min_similarity=0.30
):
    # Only retrieve approved historical resolutions.
    records = load_approved_resolutions()

    if not records:
        return []

    texts = [r["original_ticket"] for r in records]

    model = get_model()

    # Create normalized historical embeddings.
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    # Create FAISS index.
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    # Generate query embedding.
    query_embedding = model.encode(
        [ticket_text],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    # Search all records so rejected candidates do not
    # prevent finding other eligible matches.
    scores, indices = index.search(
        query_embedding,
        k=len(records)
    )

    matches = []

    for record_index, score in zip(indices[0], scores[0]):
        if record_index == -1:
            continue

        if score < min_similarity:
            continue

        record = records[record_index]

        if not safe_delivery_match(
            ticket_text,
            record["original_ticket"]
        ):
            continue

        matches.append({
            "ticket_id": record["ticket_id"],
            "original_ticket": record["original_ticket"],
            "resolution": record["resolution"],
            "similarity": float(score)
        })

        if len(matches) >= limit:
            break

    return matches
