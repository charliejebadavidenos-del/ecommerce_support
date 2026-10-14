import json
import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone


DB_PATH = Path(__file__).resolve().parent / "support_tickets.db"


def save_ticket(result: dict) -> str:
    ticket_id = str(uuid4())

    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL,
                    result_json TEXT NOT NULL
                )
            """)

            connection.execute(
                """
                INSERT INTO tickets (
                    ticket_id,
                    created_at,
                    status,
                    result_json
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    ticket_id,
                    datetime.now(timezone.utc).isoformat(),
                    "pending_review",
                    json.dumps(result, ensure_ascii=False),
                ),
            )


    return ticket_id

def load_tickets(limit: int = 100) -> list[dict]:
    if not DB_PATH.exists():
        return []

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT ticket_id, created_at, status, result_json
            FROM tickets
            ORDER BY created_at DESC, rowid DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "ticket_id": row["ticket_id"],
            "created_at": row["created_at"],
            "status": row["status"],
            "result": json.loads(row["result_json"]),
        }
        for row in rows
    ]

def resolve_ticket(ticket_id: str, resolution: str) -> None:
    resolution = resolution.strip()

    if not resolution:
        raise ValueError("Please enter the actual resolution.")

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS ticket_resolutions (
                    ticket_id TEXT PRIMARY KEY,
                    resolution TEXT NOT NULL,
                    resolved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
                )
            """)

            ticket = connection.execute(
                "SELECT status FROM tickets WHERE ticket_id = ?",
                (ticket_id,)
            ).fetchone()

            if ticket is None:
                raise ValueError("Ticket not found.")

            if ticket[0] == "resolved":
                raise ValueError("This ticket is already resolved.")

            connection.execute("""
                INSERT INTO ticket_resolutions (ticket_id, resolution)
                VALUES (?, ?)
            """, (ticket_id, resolution))

            connection.execute("""
                UPDATE tickets
                SET status = ?
                WHERE ticket_id = ?
            """, ("resolved", ticket_id))

##Resolution Text

def load_resolution(ticket_id: str) -> dict | None:
    if not DB_PATH.exists():
        return None

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row

        table_exists = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'ticket_resolutions'
        """).fetchone()

        if table_exists is None:
            return None

        row = connection.execute("""
            SELECT resolution, resolved_at, approval_status
            FROM ticket_resolutions
            WHERE ticket_id = ?
        """, (ticket_id,)).fetchone()

    return dict(row) if row else None


def approve_resolution(ticket_id: str) -> None:
    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            cursor = connection.execute("""
                UPDATE ticket_resolutions
                SET approval_status = 'approved'
                WHERE ticket_id = ?
                  AND approval_status = 'pending'
                  AND EXISTS (
                      SELECT 1 FROM tickets
                      WHERE tickets.ticket_id = ticket_resolutions.ticket_id
                        AND tickets.status = 'resolved'
                  )
            """, (ticket_id,))

            if cursor.rowcount == 0:
                raise ValueError(
                    "No pending resolution found for this resolved ticket."
                )


def load_approved_resolutions(limit: int = 100) -> list[dict]:
    if not DB_PATH.exists():
        return []

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute("""
            SELECT
                r.ticket_id,
                r.resolution,
                r.resolved_at,
                t.result_json
            FROM ticket_resolutions AS r
            JOIN tickets AS t
                ON r.ticket_id = t.ticket_id
            WHERE r.approval_status = 'approved'
              AND t.status = 'resolved'
            ORDER BY r.resolved_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [
        {
            "ticket_id": row["ticket_id"],
            "resolution": row["resolution"],
            "resolved_at": row["resolved_at"],
            "original_ticket": json.loads(
                row["result_json"]
            )["ticket_text"],
        }
        for row in rows
    ]
