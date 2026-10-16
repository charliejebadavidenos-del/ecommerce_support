
import csv
from pathlib import Path

FAQ_PATH = Path("data/faq_knowledge_base_150_1.csv")

with FAQ_PATH.open(
    encoding="utf-8-sig",
    newline=""
) as file:
    faqs = list(csv.DictReader(file))

print("Total FAQs:", len(faqs))

print("\nFirst 3 FAQs:")
for faq in faqs[:3]:
    print(
        faq["faq_id"],
        "|",
        faq["question"],
        "|",
        faq["category"]
    )



from sentence_transformers import SentenceTransformer

# Extract FAQ questions from the CSV records
faq_questions = [faq["question"] for faq in faqs]

# Load the pretrained embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Convert all FAQ questions into numerical vectors
faq_embeddings = model.encode(faq_questions)

print("\nTotal FAQ questions:", len(faq_questions))
print("FAQ embedding shape:", faq_embeddings.shape)
print("Embedding dimensions:", faq_embeddings.shape[1])



import faiss
import numpy as np

# Convert embeddings to the format required by FAISS
vectors = np.asarray(faq_embeddings, dtype="float32")

# Normalize vectors for cosine similarity search
faiss.normalize_L2(vectors)

# Create an exact inner-product index
dimension = vectors.shape[1]
index = faiss.IndexFlatIP(dimension)

# Add all FAQ embeddings to the index
index.add(vectors)

print("\nFAISS index created successfully")
print("FAISS dimension:", index.d)
print("Total vectors indexed:", index.ntotal)


# New customer question
customer_query = "Can you tell me where my parcel is?"

# Convert the customer question into an embedding
query_vector = model.encode([customer_query])

# Prepare and normalize the query vector
query_vector = np.asarray(query_vector, dtype="float32")
faiss.normalize_L2(query_vector)

# Search the 3 most similar FAQ vectors
scores, indices = index.search(query_vector, k=3)

print("\nCustomer question:", customer_query)
print("\nTop 3 semantic FAQ matches:")

for rank, (faq_index, score) in enumerate(
    zip(indices[0], scores[0]), start=1
):
    faq = faqs[int(faq_index)]

    print(f"\nRank: {rank}")
    print("FAQ ID:", faq["faq_id"])
    print("Question:", faq["question"])
    print("Category:", faq["category"])
    print("Similarity:", round(float(score), 4))


# Compare the customer query directly with FAQ001

faq001_vector = vectors[0:1]

faq001_score = np.dot(
    query_vector[0],
    faq001_vector[0]
)

print("\nExpected FAQ comparison:")
print("FAQ ID:", faqs[0]["faq_id"])
print("Question:", faqs[0]["question"])
print("Similarity:", round(float(faq001_score), 4))


###Category-aware FAISS search


# Search more candidates before applying the category filter
scores, indices = index.search(query_vector, k=index.ntotal)

target_category = "Delivery Issue"
filtered_results = []

for faq_index, score in zip(indices[0], scores[0]):
    faq = faqs[int(faq_index)]

    if faq["category"] == target_category:
        filtered_results.append((faq, float(score)))

    if len(filtered_results) == 5:
        break

print("\nTop 5 Delivery Issue FAQs:")

for rank, (faq, score) in enumerate(filtered_results, start=1):
    print(
        f"{rank}. {faq['faq_id']} | "
        f"{faq['question']} | "
        f"Similarity: {score:.4f}"
    )
