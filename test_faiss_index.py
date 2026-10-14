
import faiss
from sentence_transformers import SentenceTransformer

# Step 1: Historical tickets
historical_tickets = [
    "Where is my order?",
    "My laptop arrived damaged.",
    "I was charged twice for my purchase."
]

# Step 2: Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Step 3: Generate normalized embeddings
embeddings = model.encode(
    historical_tickets,
    convert_to_numpy=True,
    normalize_embeddings=True
).astype("float32")

# Step 4: Identify vector dimensions
dimension = embeddings.shape[1]

# Step 5: Create FAISS index
index = faiss.IndexFlatIP(dimension)

# Step 6: Add embeddings to FAISS
index.add(embeddings)

print("Embedding dimensions:", dimension)
print("Total vectors indexed:", index.ntotal)
print("FAISS index created successfully")



# Step 8: New customer query
query = "Can you track my parcel?"

# Convert the query into a normalized vector
query_embedding = model.encode(
    [query],
    convert_to_numpy=True,
    normalize_embeddings=True
).astype("float32")

# Search for the top 3 similar historical tickets
scores, indices = index.search(query_embedding, k=3)

print("\nNew customer ticket:", query)
print("\nTop 3 similar historical tickets:")

for rank, (ticket_index, score) in enumerate(
    zip(indices[0], scores[0]),
    start=1
):
    print(
        f"Rank {rank}: {historical_tickets[ticket_index]}"
        f" | Similarity: {score:.4f}"
    )



# Step 9: Apply a minimum similarity threshold

MIN_SIMILARITY = 0.30

print("\nMatches passing similarity threshold:")

accepted_matches = []

for ticket_index, score in zip(indices[0], scores[0]):
    if ticket_index == -1:
        continue

    if score >= MIN_SIMILARITY:
        accepted_matches.append({
            "ticket": historical_tickets[ticket_index],
            "similarity": float(score)
        })

if accepted_matches:
    for match in accepted_matches:
        print(
            f"Ticket: {match['ticket']}"
            f" | Similarity: {match['similarity']:.4f}"
        )
else:
    print("No sufficiently similar historical tickets found.")
    print("Human review or FAQ retrieval is required.")



# Step 9B: Negative test with an unrelated query

unrelated_query = "How do I change my account password?"

unrelated_embedding = model.encode(
    [unrelated_query],
    convert_to_numpy=True,
    normalize_embeddings=True
).astype("float32")

scores_negative, indices_negative = index.search(
    unrelated_embedding,
    k=3
)

print("\nNegative test query:", unrelated_query)

negative_matches = []

for ticket_index, score in zip(
    indices_negative[0],
    scores_negative[0]
):
    if ticket_index == -1:
        continue

    print(
        f"{historical_tickets[ticket_index]}"
        f" | Similarity: {score:.4f}"
    )

    if score >= MIN_SIMILARITY:
        negative_matches.append(
            historical_tickets[ticket_index]
        )

if negative_matches:
    print("WARNING: Unrelated query produced accepted matches.")
else:
    print("PASS: No unrelated historical tickets accepted.")



# Step 9C: Contradiction test

contradiction_sentences = [
    "My order was delivered.",
    "My order was not delivered."
]

contradiction_embeddings = model.encode(
    contradiction_sentences,
    convert_to_numpy=True,
    normalize_embeddings=True
).astype("float32")

similarity = float(
    contradiction_embeddings[0] @ contradiction_embeddings[1]
)

print("\nContradiction test:")
print("Sentence 1:", contradiction_sentences[0])
print("Sentence 2:", contradiction_sentences[1])
print(f"Cosine similarity: {similarity:.4f}")

if similarity >= MIN_SIMILARITY:
    print("WARNING: Contradictory sentences pass the similarity threshold.")
    print("Additional contradiction safeguards are required.")
else:
    print("Contradictory sentences fall below the threshold.")
