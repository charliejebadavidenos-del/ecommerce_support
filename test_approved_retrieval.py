
import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import storage

with tempfile.TemporaryDirectory() as folder:
    test_db = Path(folder) / "test_support.db"

    with sqlite3.connect(test_db) as conn:
        conn.executescript("""
            CREATE TABLE tickets (
                ticket_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                result_json TEXT NOT NULL
            );

            CREATE TABLE ticket_resolutions (
                ticket_id TEXT PRIMARY KEY,
                resolution TEXT NOT NULL,
                resolved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                approval_status TEXT NOT NULL
            );
        """)

        conn.execute(
            "INSERT INTO tickets VALUES (?, ?, ?)",
            (
                "TEST001",
                "resolved",
                json.dumps({
                    "ticket_text": "Where is my order?"
                }),
            ),
        )

        conn.execute(
            """INSERT INTO ticket_resolutions
               (ticket_id, resolution, approval_status)
               VALUES (?, ?, ?)""",
            (
                "TEST001",
                "DEMO ONLY: Tracking instructions verified.",
                "approved",
            ),
        )

    conn.close()

    with patch.object(storage, "DB_PATH", test_db):
        results = storage.load_approved_resolutions()


    assert len(results) == 1
    assert results[0]["ticket_id"] == "TEST001"

    print("Approved retrieval test: PASSED")
    print(results)
