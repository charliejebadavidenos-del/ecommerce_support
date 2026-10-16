
import json
import sqlite3

TEST_DB = "support_tickets_learning_test.db"

test_cases = [
    (
        "TEST1001",
        "My order arrived damaged. I need a replacement.",
        "Arrange a replacement after verifying the damage."
    ),
    (
        "TEST1002",
        "My package was damaged during delivery.",
        "Ask the customer to contact the support team."
    ),
    (
        "TEST1003",
        "My order has not arrived yet. Where is it?",
        "Check the shipment tracking and provide an update."
    )
]

connection = sqlite3.connect(TEST_DB)

try:
    with connection:
        for ticket_id, ticket_text, resolution in test_cases:
            result_json = json.dumps({
                "ticket_text": ticket_text
            })

            connection.execute("""
                INSERT OR IGNORE INTO tickets (
                    ticket_id,
                    status,
                    result_json
                )
                VALUES (?, 'resolved', ?)
            """, (ticket_id, result_json))

            connection.execute("""
                INSERT OR IGNORE INTO ticket_resolutions (
                    ticket_id,
                    resolution,
                    approval_status
                )
                VALUES (?, ?, 'approved')
            """, (ticket_id, resolution))

    print("Synthetic test tickets prepared.")

    rows = connection.execute("""
        SELECT t.ticket_id, r.approval_status
        FROM tickets AS t
        JOIN ticket_resolutions AS r
            ON t.ticket_id = r.ticket_id
        WHERE t.ticket_id LIKE 'TEST%'
        ORDER BY t.ticket_id
    """).fetchall()

    for row in rows:
        print(row)

finally:
    connection.close()
