
from learning_agent import calculate_learning_score

# Simulated FAISS matches
matches = [
    {
        "ticket_id": "H001",
        "similarity": 0.90,
        "helpful": 0,
        "not_helpful": 5
    },
    {
        "ticket_id": "H002",
        "similarity": 0.85,
        "helpful": 5,
        "not_helpful": 0
    },
    {
        "ticket_id": "H003",
        "similarity": 0.80,
        "helpful": 0,
        "not_helpful": 0
    }
]

for match in matches:
    match["learning_score"] = calculate_learning_score(
        similarity=match["similarity"],
        helpful=match["helpful"],
        not_helpful=match["not_helpful"]
    )

matches.sort(
    key=lambda item: item["learning_score"],
    reverse=True
)

for rank, match in enumerate(matches, start=1):
    print(
        f"Rank {rank}: {match['ticket_id']} "
        f"| Similarity: {match['similarity']} "
        f"| Learning Score: {match['learning_score']}"
    )

assert [m["ticket_id"] for m in matches] == [
    "H002", "H001", "H003"
]

print("Learning ranking test PASSED")
