
from transformers import pipeline

# Step 1: Load pretrained sentiment model
model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"

sentiment_model = pipeline(
    task="text-classification",
    model=model_name,
    device=-1  # Use CPU
)

# Step 2: Sample customer tickets
tickets = [
    "I am extremely disappointed with the delayed delivery.",
    "Thank you! My refund was processed very quickly.",
    "I would like to know the status of my order.",
    "The product is damaged and I am not happy.",
    "The customer support team was very helpful."
]

# Step 3: Predict sentiment
for ticket in tickets:
    result = sentiment_model(ticket)[0]

    print("\nTicket:", ticket)
    print("Sentiment:", result["label"])
    print("Confidence:", round(result["score"], 4))
