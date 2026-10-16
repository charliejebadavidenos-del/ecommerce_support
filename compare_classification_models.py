
import time
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# 1. Load and deduplicate the dataset
df = pd.read_csv("data/support_tickets_10k.csv")
df = df.drop_duplicates(subset=["ticket_text"]).copy()

X = df["ticket_text"]
y = df["ticket_category"]

# 2. Use the same train/test split for both models
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# 3. Define the models
models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
}

results = []

# 4. Train and evaluate both models
for name, classifier in models.items():

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2)
        )),
        ("classifier", classifier)
    ])

    start = time.perf_counter()
    pipeline.fit(X_train, y_train)
    training_time = time.perf_counter() - start

    start = time.perf_counter()
    predictions = pipeline.predict(X_test)
    prediction_time = time.perf_counter() - start

    results.append({
        "Model": name,
        "Accuracy": round(accuracy_score(y_test, predictions), 4),
        "Precision": round(precision_score(
            y_test, predictions,
            average="macro", zero_division=0
        ), 4),
        "Recall": round(recall_score(
            y_test, predictions,
            average="macro", zero_division=0
        ), 4),
        "F1 Score": round(f1_score(
            y_test, predictions,
            average="macro", zero_division=0
        ), 4),
        "Training Time (s)": round(training_time, 3),
        "Prediction Time (s)": round(prediction_time, 3)
    })

# 5. Display comparison
comparison = pd.DataFrame(results)

print("\nMODEL COMPARISON")
print(comparison.to_string(index=False))

# 6. Save results for project documentation
comparison.to_csv(
    "model_comparison_results.csv",
    index=False
)

print("\nResults saved to model_comparison_results.csv")
