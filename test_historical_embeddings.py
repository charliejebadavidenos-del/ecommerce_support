
from sentence_transformers import SentenceTransformer

# Simulated approved historical tickets.
# These are test records, not actual database records.
historical_tickets = [
    {
        "ticket_id": "DEMO001",
        "original_ticket": "Where is my order?",
        "resolution": "Customer was provided tracking instructions."
    },
    {
        "ticket_id": "DEMO002",
        "original_ticket": "My laptop arrived damaged.",
        "resolution": "Customer was guided through replacement procedures."
    },
    {
        "ticket_id": "DEMO003",
        "original_ticket": "I was charged twice for my purchase.",
        "resolution": "Payment team reviewed the duplicate charge."
    }
]

model = SentenceTransformer("all-MiniLM-L6-v2")

ticket_texts = [
    ticket["original_ticket"]
    for ticket in historical_tickets
]

embeddings = model.encode(
    ticket_texts,
    convert_to_numpy=True,
    normalize_embeddings=True
)

print("Historical tickets:", len(historical_tickets))
print("Embedding shape:", embeddings.shape)
print("Embedding dimensions:", embeddings.shape[1])

for index, ticket in enumerate(historical_tickets):
    print(
        ticket["ticket_id"],
        "|",
        ticket["original_ticket"],
        "| Vector shape:",
        embeddings[index].shape
    )
