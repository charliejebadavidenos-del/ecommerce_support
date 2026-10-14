
import csv
from agents.retrieval_agent import FAQ_PATH

new_faqs = [
    {
        "faq_id": "FAQ151",
        "question": "How do I report being charged twice for the same order?",
        "answer": (
            "If you believe you were charged twice, contact Payment Support "
            "with your order ID and relevant payment transaction references. "
            "The team will review the transactions and advise on next steps. "
            "Do not share your card number, CVV, PIN, or OTP."
        ),
        "category": "Payment Issue",
    },
    {
        "faq_id": "FAQ152",
        "question": "How do I request a refund for my order?",
        "answer": (
            "To request a refund, contact Returns and Refunds Support "
            "with your order ID and reason for the request. "
            "The team will review your request against the applicable "
            "refund policy and advise on eligibility and next steps."
        ),
        "category": "Refund & Return",
    },
]

with FAQ_PATH.open(
    encoding="utf-8-sig",
    newline=""
) as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    rows = list(reader)

existing_ids = {row["faq_id"] for row in rows}

for faq in new_faqs:
    if faq["faq_id"] not in existing_ids:
        rows.append(faq)
        print("Added:", faq["faq_id"])
    else:
        print("Already exists:", faq["faq_id"])

with FAQ_PATH.open(
    "w",
    encoding="utf-8-sig",
    newline=""
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )
    writer.writeheader()
    writer.writerows(rows)

print("Total FAQs:", len(rows))
