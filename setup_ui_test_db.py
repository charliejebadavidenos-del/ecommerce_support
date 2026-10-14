
import json
import sqlite3
from pathlib import Path

test_db = Path("support_tickets_ui_test.db")

if test_db.exists():
    raise SystemExit(
        "Test database already exists. "
        "Stopping to avoid overwriting it."
    )

with sqlite3.connect(test_db) as conn:
    conn.execute("""
        CREATE TABLE tickets (
            ticket_id TEXT PRIMARY KEY,
            created_at TEXT,
            status TEXT,
            result_json TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE ticket_resolutions (
            ticket_id TEXT PRIMARY KEY,
            resolution TEXT,
            resolved_at TEXT,
            approval_status TEXT
        )
    """)

    conn.execute(
        "INSERT INTO tickets VALUES (?, ?, ?, ?)",
        (
            "DEMO001",
            "2026-10-14",
            "resolved",
            json.dumps({
                "ticket_text": "Where is my order?",
                "category": "Delivery",
                "priority": "Medium",
            }),
        ),
    )

    conn.execute(
        "INSERT INTO ticket_resolutions VALUES (?, ?, ?, ?)",
        (
            "DEMO001",
            "DEMO ONLY: Tracking instructions verified.",
            "2026-10-14",
            "approved",
        ),
    )

print("UI test database created:", test_db)
