
from unittest.mock import patch
import resolution_matcher

historical_resolutions = [
    {
        "ticket_id": "TEST003",
        "original_ticket": "I received my order",
        "resolution": "DEMO: Delivery confirmed.",
        "resolved_at": "2026-10-14",
    }
]

with patch.object(
    resolution_matcher,
    "load_approved_resolutions",
    return_value=historical_resolutions,
):
    results = resolution_matcher.match_approved_resolutions(
        "I did not receive my order",
        min_similarity=0.0,
    )

assert results == [], "Opposite delivery statements must not match"

print("Negation safeguard test: PASSED")
print("Matches found:", len(results))
