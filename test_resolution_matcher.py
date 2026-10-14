
from unittest.mock import patch
import resolution_matcher

sample_resolutions = [
    {
        "ticket_id": "TEST001",
        "original_ticket": "Where is my order?",
        "resolution": "DEMO: Provided tracking instructions.",
        "resolved_at": "2026-10-14",
    },
    {
        "ticket_id": "TEST002",
        "original_ticket": "My laptop arrived broken",
        "resolution": "DEMO: Explained replacement process.",
        "resolved_at": "2026-10-14",
    },
]

with patch.object(
    resolution_matcher,
    "load_approved_resolutions",
    return_value=sample_resolutions,
):
    results = resolution_matcher.match_approved_resolutions(
        "Where is my order?",
        min_similarity=0.5,
    )

assert len(results) == 1
assert results[0]["ticket_id"] == "TEST001"

print("Similarity matching test: PASSED")
print("Matched ticket:", results[0]["ticket_id"])
print("Similarity score:", results[0]["similarity"])
