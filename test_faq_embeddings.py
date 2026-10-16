
from sentence_transformers import SentenceTransformer

# Load a pretrained sentence embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "I would like to know my order status",
    "How do I track my order?",
    "How do I reset my password?"
]

# Convert text into numerical vectors
embeddings = model.encode(sentences)

print("Number of sentences:", len(sentences))
print("Embedding shape:", embeddings.shape)
print("Dimensions per sentence:", embeddings.shape[1])


from sklearn.metrics.pairwise import cosine_similarity

similarities = cosine_similarity(embeddings)

print("\nCosine similarity matrix:")
print(similarities.round(3))

print("\nOrder status vs Order tracking:",
      round(float(similarities[0][1]), 3))

print("Order status vs Password reset:",
      round(float(similarities[0][2]), 3))



import faiss
import numpy as np

# Normalize embeddings so inner product equals cosine similarity
vectors = np.asarray(embeddings, dtype="float32")
faiss.normalize_L2(vectors)

# Create a FAISS index
dimension = vectors.shape[1]
index = faiss.IndexFlatIP(dimension)

# Store all three sentence vectors
index.add(vectors)

print("\nFAISS vectors stored:", index.ntotal)

# Search using the first sentence
query = vectors[0:1]

scores, indices = index.search(query, k=3)

print("\nFAISS search results:")
for rank, (idx, score) in enumerate(
    zip(indices[0], scores[0]), start=1
):
    print(
        f"Rank {rank}: {sentences[idx]} "
        f"| Similarity: {score:.3f}"
    )

