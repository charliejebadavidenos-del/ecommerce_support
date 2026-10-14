
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from storage import load_approved_resolutions
from test_delivery_safety import safe_delivery_match


_model = None


# Cache for approved historical ticket embeddings and FAISS index.
_cached_index = None
_cached_records = []
_cached_signature = None



def get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


def get_cached_index(records):
    global _cached_index, _cached_records, _cached_signature

    # Detect changes to approved historical records.
    signature = tuple(
        (
            r["ticket_id"],
            r["original_ticket"],
            r["resolution"]
        )
        for r in records
    )

    # Reuse the existing index when records have not changed.
    if signature == _cached_signature:
        return _cached_index, _cached_records

    # No approved records: clear the cache.
    if not records:
        _cached_index = None
        _cached_records = []
        _cached_signature = signature
        return None, []

    # Generate embeddings for approved historical tickets.
    texts = [r["original_ticket"] for r in records]

    embeddings = get_model().encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    # Build FAISS index using normalized vectors.
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    # Store the completed index and corresponding records.
    _cached_index = index
    _cached_records = list(records)
    _cached_signature = signature

    return _cached_index, _cached_records

def match_semantic_resolutions(
    ticket_text,
    limit=3,
    min_similarity=0.30
):
    # Only retrieve approved historical resolutions.
    records = load_approved_resolutions()

    if not records:
        return []

    
    # Reuse cached historical embeddings and FAISS index.
    index, records = get_cached_index(records)

    if index is None:
        return []

    model = get_model()

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
