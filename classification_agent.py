from pathlib import Path
from functools import lru_cache

import joblib


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "ticket_classifier_lr.joblib"
)


@lru_cache(maxsize=1)
def load_classification_model():
    return joblib.load(MODEL_PATH)


def predict_ticket_category(ticket_text: str) -> str:
    if not ticket_text or not ticket_text.strip():
        return "Needs Review"

    model = load_classification_model()
    return str(model.predict([ticket_text])[0])

def classify_ticket(intent: str) -> dict:
    routing = {
        "delivery_status": {
            "category": "Delivery",
            "team": "Delivery Support",
        },
        "request_refund": {
            "category": "Refund",
            "team": "Returns and Refunds",
        },
        "payment_problem": {
            "category": "Payment",
            "team": "Payment Support",
        },
        "report_product_issue": {
            "category": "Product Issue",
            "team": "Product Support",
        },

        "request_replacement": {
            "category": "Product Issue",
            "team": "Product Support",
        },
        "wrong_item_received": {
            "category": "Product Issue",
            "team": "Product Support",
        },



    }

    return routing.get(
        intent,
        {
            "category": "Needs Review",
            "team": "General Support",
        },
    )

def assign_priority(text: str, intent: str) -> str:
    text = text.casefold()

    high_priority_phrases = [
        "unauthorized payment",
        "charged twice",
        "urgent",
        "paid twice",
    ]

    if any(phrase in text for phrase in high_priority_phrases):
        return "High"

    if intent == "delivery_status":
        missing_delivery = any(
            phrase in text
            for phrase in ["not arrived", "not delivered"]
        )

        if not missing_delivery:
            return "Low"

    return "Medium"