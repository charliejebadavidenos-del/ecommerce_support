
from pathlib import Path
import sqlite3
import storage

# Use only the isolated test database.
storage.DB_PATH = Path("support_tickets_ui_test.db")

# Create a test ticket.
ticket_id = storage.save_ticket({
    "ticket_text": "Timestamp verification test",
    "intent": "test",
    "category": "Test"
})

# Read the saved timestamp.
with sqlite3.connect(storage.DB_PATH) as connection:
    row = connection.execute(
        """
        SELECT ticket_id, created_at
        FROM tickets
        WHERE ticket_id = ?
        """,
        (ticket_id,)
    ).fetchone()

print("Saved ticket:", row[0] if row else None)
print("Created at:", row[1] if row else None)

assert row is not None, "Ticket was not saved"
assert row[1] is not None, "Timestamp is missing"

print("PASS: Ticket timestamp saved successfully")
