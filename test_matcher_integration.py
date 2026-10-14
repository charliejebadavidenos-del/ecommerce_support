
import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import storage
from resolution_matcher import match_approved_resolutions

with tempfile.TemporaryDirectory() as temp_dir:
    test_db = Path(temp_dir) / "test_tickets.db"

    with patch.object(storage, "DB_PATH", test_db):
        conn = sqlite3.connect(test_db)

        try:
            conn.execute("""
                CREATE TABLE tickets (
                    ticket_id TEXT PRIMARY KEY,
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
                "INSERT INTO tickets VALUES (?, ?, ?)",
                (
                    "TEST100",
                    "resolved",
                    json.dumps({
                        "ticket_text": "Where is my order?"
                    }),
                ),
            )

            conn.execute(
                "INSERT INTO ticket_resolutions VALUES (?, ?, ?, ?)",
                (
                    "TEST100",
                    "DEMO: Customer was given tracking instructions.",
                    "2026-10-14",
                    "approved",
                ),
            )

            conn.commit()
        finally:
            conn.close()

        matches = match_approved_resolutions(
            "Where is my package?"
        )

        assert len(matches) == 1
        assert matches[0]["ticket_id"] == "TEST100"
        assert matches[0]["similarity"] == 1.0

        print("SQLite matcher integration test: PASSED")
        print("Matched ticket:", matches[0]["ticket_id"])
        print("Similarity:", matches[0]["similarity"])
        print("Resolution:", matches[0]["resolution"])
