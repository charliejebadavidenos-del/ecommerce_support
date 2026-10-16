import re


def clean_ticket(text: str) -> str:
    """Remove extra whitespace while preserving the message."""
    return " ".join(text.split())


def extract_order_id(text: str) -> str | None:
    # Example: ORD12890
    match = re.search(r"\bORD\d+\b", text, flags=re.IGNORECASE)
    if match:
        return match.group(0).upper()

    # Examples: order 12890, order ID: 12890, order #12890
    match = re.search(
        r"\border\s+(?:(?:id|number)\s*)?[:#]?\s*(\d+)\b",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1)

    return None

def detect_intent(text: str) -> str:
    text = text.casefold()

    rules = {
        "delivery_status": [
            "not arrived",
            "not delivered",
            "where is my order",
            "track my order",
            "track a gift order",
            "didnt receive",
            "didn't receive",
            "did not receive",
            "never received",
            "missing delivery",
            "where is my package",
            "where is my parcel",
            "track my package",
            "delivery status",
            "order status",
        ],
        "request_refund": [
            "want a refund",
            "request a refund",
            "money back",
        ],
        "payment_problem": [
            "charged twice",
            "paid twice",
            "payment failed",
            "payment declined",
        ],
        "report_product_issue": [
            "arrived damaged",
            "broken",
            "not working",
        ],
        "request_replacement": [
            "need a replacement",
            "want a replacement",
            "request a replacement",
            "replace my",
            "exchange my",
        ],
        "wrong_item_received": [
            "received the wrong",
            "wrong item",
            "wrong product",
            "incorrect item",
            "different product",
            "not what i ordered",
            "didnt receive what i ordered",
            "didn't receive what i ordered",
            "did not receive what i ordered",
        ],

    }

    matches = [
        intent
        for intent, phrases in rules.items()
        if any(phrase in text for phrase in phrases)
    ]

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:

        if "wrong_item_received" in matches:
            return "wrong_item_received"

        if (
            "report_product_issue" in matches
            and "request_replacement" in matches
        ):
            return "request_replacement"

        return "multiple_intents"

    return "unknown"

def detect_sentiment(text: str) -> str:
    text = clean_ticket(text).casefold()

    negative_phrases = (
        "i am angry",
        "i'm angry",
        "i am frustrated",
        "i'm frustrated",
        "very disappointed",
        "terrible service",
        "unacceptable",
    )

    positive_phrases = (
        "great service",
        "very satisfied",
        "excellent support",
    )

    def contains_phrase(phrases):
        return any(
            re.search(r"\b" + re.escape(phrase) + r"\b", text)
            for phrase in phrases
        )

    if contains_phrase(negative_phrases):
        return "negative"

    if contains_phrase(positive_phrases):
        return "positive"

    return "neutral"


def extract_product(text: str) -> str | None:
    """Extract a product mentioned after a supported action phrase."""
    product_pattern = (
        r"\b(?:ordered|bought|purchased)\s+"
        r"(?:a|an|the)?\s*"
        r"(.+?)"
        r"(?=,|\.|\s+(?:because|but|and\s+(?:it|the))\b|$)"
    )

    match = re.search(
        product_pattern,
        text,
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return None


if __name__ == "__main__":
    ticket = input("Enter your support ticket: ")

    cleaned_text = clean_ticket(ticket)

    if not cleaned_text:
        print("Please enter a non-empty ticket.")
    else:
        print("\nCleaned ticket:")
        print(cleaned_text)