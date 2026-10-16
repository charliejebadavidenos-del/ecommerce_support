
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

# Step 1: Load dataset
df = pd.read_csv("data/support_tickets_10k.csv")

# Step 2: Define features and target
X = df["ticket_text"]
y = df["ticket_category"]

# Step 3: Split dataset (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

# Step 4: Build TF-IDF + Logistic Regression pipeline
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

# Step 5: Train model
model.fit(X_train, y_train)

# Step 6: Evaluate model
predictions = model.predict(X_test)

print("\nAccuracy:", round(
    accuracy_score(y_test, predictions), 4
))

print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))
