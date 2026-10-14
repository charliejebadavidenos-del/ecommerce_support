
from pathlib import Path
import storage

from semantic_resolution_matcher import match_semantic_resolutions

# Use the isolated test database.
storage.DB_PATH = Path("support_tickets_ui_test.db")

query = "Where is my order?"

matches = match_semantic_resolutions(
    ticket_text=query,
    limit=3,
    min_similarity=0.30
)

print("Customer query:", query)
print("Number of matches:", len(matches))

for match in matches:
    print("Ticket ID:", match["ticket_id"])
    print("Original ticket:", match["original_ticket"])
    print("Resolution:", match["resolution"])
    print("Similarity:", round(match["similarity"], 4))
