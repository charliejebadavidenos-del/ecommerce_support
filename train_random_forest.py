
import pandas as pd
import joblib
from pathlib import Path


from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    classification_report
)

# Load original dataset
df = pd.read_csv("data/support_tickets_10k.csv")

# Remove identical customer ticket texts
df = df.drop_duplicates(subset=["ticket_text"]).copy()

print("Unique tickets:", len(df))

X = df["ticket_text"]
y = df["ticket_category"]

# Stratified train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2)
    )),
    ("classifier", RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    ))
])

model.fit(X_train, y_train)

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


# Save trained TF-IDF + Random Forest pipeline
Path("models").mkdir(exist_ok=True)

joblib.dump(
    model,
    "models/ticket_classifier_rf.joblib"
)

print("Model saved successfully.")