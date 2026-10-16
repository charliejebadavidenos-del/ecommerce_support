
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

df = pd.read_csv("data/support_tickets_10k.csv")
df = df.drop_duplicates(subset=["ticket_text"])

X_train, X_test, y_train, y_test = train_test_split(
    df["ticket_text"],
    df["ticket_category"],
    test_size=0.20,
    random_state=42,
    stratify=df["ticket_category"]
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2)
    )),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ))
])

model.fit(X_train, y_train)

test_tickets = [
    "I cannot log into my account after changing my password.",
    "The delivery person marked my package as delivered, but I never received it.",
    "My credit card was charged twice for the same purchase.",
    "The blender I bought stopped working after two days.",
    "The shopping app crashes whenever I try to open my cart."
]

print("\nCUSTOM CLASSIFICATION RESULTS")

for ticket, prediction in zip(
    test_tickets,
    model.predict(test_tickets)
):
    print("\nTicket:", ticket)
    print("Predicted category:", prediction)
