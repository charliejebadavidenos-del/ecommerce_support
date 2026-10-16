
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Load deduplicated training data
df = pd.read_csv("data/support_tickets_10k.csv")
df = df.drop_duplicates(subset=["ticket_text"])

X_train, X_test, y_train, y_test = train_test_split(
    df["ticket_text"],
    df["ticket_category"],
    test_size=0.20,
    random_state=42,
    stratify=df["ticket_category"]
)

# Train Logistic Regression
lr_model = Pipeline([
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

lr_model.fit(X_train, y_train)

# Load previously saved Random Forest
rf_model = joblib.load(
    "models/ticket_classifier_rf.joblib"
)

# Independently written customer complaints
tickets = [
    "My credit card was charged twice for the same order",
    "My payment was deducted twice for the same order",
    "I was charged twice and need a refund",
    "My payment failed during checkout",
    "I want to return my product and receive a refund"
]

print("\nMODEL GENERALIZATION COMPARISON")

for ticket in tickets:
    lr_prediction = lr_model.predict([ticket])[0]
    rf_prediction = rf_model.predict([ticket])[0]

    print("\nTicket:", ticket)
    print("Logistic Regression:", lr_prediction)
    print("Random Forest:", rf_prediction)
