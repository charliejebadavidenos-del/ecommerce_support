
from pathlib import Path
import storage
from workflow import workflow

# Use the isolated test database.
storage.DB_PATH = Path("support_tickets_ui_test.db")

# Run the full LangGraph workflow.
result = workflow.invoke({
    "ticket_text": "Where is my order?"
})

print("Customer ticket:", result["ticket_text"])
print("Intent:", result.get("intent"))
print("Suggested resolutions:", len(
    result.get("suggested_resolutions", [])
))

for match in result.get("suggested_resolutions", []):
    print("Ticket ID:", match["ticket_id"])
    print("Resolution:", match["resolution"])
    print("Similarity:", round(match["similarity"], 4))
