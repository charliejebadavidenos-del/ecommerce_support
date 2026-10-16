
from pathlib import Path

import storage

# Redirect database access before importing the agents.
storage.DB_PATH = Path(
    "support_tickets_learning_test.db"
).resolve()

import learning_agent
import semantic_resolution_matcher

learning_agent.DB_PATH = storage.DB_PATH

#query = "My order arrived damaged. I need a replacement."
query = "The product I received is broken. Can you replace it?"

matches = (
    semantic_resolution_matcher.match_semantic_resolutions(
        query,
        limit=3
    )
)

print("Database:", storage.DB_PATH)
print("Matches found:", len(matches))

for rank, match in enumerate(matches, start=1):
    print(
        f"Rank {rank}: {match['ticket_id']}"
        f" | Similarity: {match['similarity']:.4f}"
        f" | Learning score: {match['learning_score']:.4f}"
        f" | Helpful: {match['helpful_feedback']}"
        f" | Not helpful: {match['not_helpful_feedback']}"
    )

assert matches, "Expected at least one approved match."

assert all(
    "learning_score" in match
    for match in matches
), "Learning score is missing."

assert all(
    matches[i]["learning_score"]
    >= matches[i + 1]["learning_score"]
    for i in range(len(matches) - 1)
), "Matches are not sorted by learning score."

print("FAISS learning integration test PASSED")
