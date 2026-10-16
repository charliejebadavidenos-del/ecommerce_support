
import math

from storage import load_approved_resolutions


def get_learning_memory():
    """
    Load only human-approved ticket-resolution pairs.
    Pending resolutions must never enter learning memory.
    """
    records = load_approved_resolutions()

    memory = []

    for record in records:
        ticket_text = record.get("original_ticket")
        resolution = record.get("resolution")

        if not isinstance(ticket_text, str):
            continue

        if not isinstance(resolution, str):
            continue

        if not ticket_text.strip() or not resolution.strip():
            continue

        memory.append({
            "ticket_id": record["ticket_id"],
            "ticket_text": ticket_text,
            "resolution": resolution
        })

    return memory


def get_learning_status():
    """
    Return the number of approved examples available
    for learning.
    """
    memory = get_learning_memory()

    return {
        "approved_examples": len(memory),
        "learning_ready": len(memory) > 0
    }


##Create the feedback table
import sqlite3
from contextlib import closing
from storage import DB_PATH


def initialize_learning_feedback():
    """
    Create the feedback table for the Advanced Learning Agent.
    Existing ticket and resolution records are preserved.
    """
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS retrieval_feedback (
                    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_ticket_id TEXT NOT NULL,
                    historical_ticket_id TEXT NOT NULL,
                    feedback TEXT NOT NULL
                        CHECK (feedback IN ('helpful', 'not_helpful')),
                    created_at TEXT NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (query_ticket_id)
                        REFERENCES tickets(ticket_id),
                    FOREIGN KEY (historical_ticket_id)
                        REFERENCES ticket_resolutions(ticket_id)
                )
            """)

## Implement feedback recording

def record_retrieval_feedback(
    query_ticket_id: str,
    historical_ticket_id: str,
    feedback: str
) -> int:
    """
    Record human feedback for an approved historical resolution.

    Returns the new feedback record ID.
    """

    if feedback not in ("helpful", "not_helpful"):
        raise ValueError(
            "Feedback must be 'helpful' or 'not_helpful'."
        )

    if query_ticket_id == historical_ticket_id:
        raise ValueError(
            "A ticket cannot provide retrieval feedback about itself."
        )

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        with connection:
            approved = connection.execute("""
                SELECT 1
                FROM ticket_resolutions AS r
                JOIN tickets AS t
                    ON t.ticket_id = r.ticket_id
                WHERE r.ticket_id = ?
                  AND r.approval_status = 'approved'
                  AND t.status = 'resolved'
            """, (historical_ticket_id,)).fetchone()

            if approved is None:
                raise ValueError(
                    "Historical resolution is not approved."
                )

            query_exists = connection.execute("""
                SELECT 1
                FROM tickets
                WHERE ticket_id = ?
            """, (query_ticket_id,)).fetchone()

            if query_exists is None:
                raise ValueError("Query ticket not found.")

            cursor = connection.execute("""
                INSERT INTO retrieval_feedback (
                    query_ticket_id,
                    historical_ticket_id,
                    feedback
                )
                VALUES (?, ?, ?)
            """, (
                query_ticket_id,
                historical_ticket_id,
                feedback
            ))

            return cursor.lastrowid

##Add Feedback Summary Function
def get_retrieval_feedback_summary(
    historical_ticket_id: str
) -> dict:
    """
    Count helpful and not-helpful feedback
    for an approved historical resolution.
    """

    with closing(sqlite3.connect(DB_PATH)) as connection:
        row = connection.execute("""
            SELECT
                SUM(CASE WHEN f.feedback = 'helpful'
                    THEN 1 ELSE 0 END),
                SUM(CASE WHEN f.feedback = 'not_helpful'
                    THEN 1 ELSE 0 END)
            FROM retrieval_feedback AS f
            JOIN ticket_resolutions AS r
                ON f.historical_ticket_id = r.ticket_id
            JOIN tickets AS t
                ON r.ticket_id = t.ticket_id
            WHERE f.historical_ticket_id = ?
              AND r.approval_status = 'approved'
              AND t.status = 'resolved'
        """, (historical_ticket_id,)).fetchone()

    helpful = row[0] or 0
    not_helpful = row[1] or 0

    return {
        "historical_ticket_id": historical_ticket_id,
        "helpful": helpful,
        "not_helpful": not_helpful,
        "total_feedback": helpful + not_helpful
    }

##Add Ranking Function


def calculate_learning_score(
    similarity: float,
    helpful: int,
    not_helpful: int
) -> float:
    """
    Calculate a feedback-adjusted similarity score.

    Feedback has a limited influence on ranking.
    """


    if not math.isfinite(similarity):
        raise ValueError("Similarity must be finite.")

    if not -0.000001 <= similarity <= 1.000001:
        raise ValueError("Similarity must be between 0 and 1.")

    similarity = max(0.0, min(1.0, similarity))

    if helpful < 0 or not_helpful < 0:
        raise ValueError("Feedback counts cannot be negative.")

    feedback_adjustment = (
        0.10 * (helpful - not_helpful)
        / (helpful + not_helpful + 2)
    )

    adjusted_score = similarity + feedback_adjustment

    return round(
        max(0.0, min(1.0, adjusted_score)),
        4
    )
