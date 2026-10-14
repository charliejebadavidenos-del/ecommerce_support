
from sentence_transformers import SentenceTransformer

# Load the pretrained embedding model.
model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "Where is my package?",
    "Can you track my parcel?",
    "I want a refund for my damaged product."
]

# Convert sentences into numerical vectors.
embeddings = model.encode(sentences)

print("Number of sentences:", len(sentences))
print("Embedding shape:", embeddings.shape)
print("Vector dimensions:", embeddings.shape[1])
print("First 5 values:", embeddings[0][:5])
