
import numpy as np
from sentence_transformers import SentenceTransformer
from storage import load_approved_resolutions

# Step 1: Load approved historical resolutions.
records = load_approved_resolutions()

print("Approved historical records:", len(records))

if not records:
    print("No approved resolutions available.")
    print("No embeddings generated.")
else:
    # Step 2: Extract original customer ticket text.
    ticket_texts = [
        record["original_ticket"]
        for record in records
    ]

    # Step 3: Load the embedding model.
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Step 4: Generate embeddings.
    embeddings = model.encode(
        ticket_texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    print("Embedding shape:", embeddings.shape)
    print("Embedding dimensions:", embeddings.shape[1])
    print("Ticket IDs:", [r["ticket_id"] for r in records])
