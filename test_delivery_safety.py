
import re


def delivery_status(text):
    text = text.lower()

    # Check negative delivery statements first.
    if re.search(
        r"\b(not delivered|never delivered|wasn't delivered|"
        r"was not delivered|hasn't arrived|has not arrived|"
        r"didn't arrive|did not arrive|"
        r"haven't received (?:my|the) (?:order|parcel|package)|"
        r"have not received (?:my|the) (?:order|parcel|package)|"
        r"hasn't received (?:my|the) (?:order|parcel|package))\b",
        text
    ):
        return "NOT_DELIVERED"

    # Check positive delivery statements.
    # Check positive delivery statements.
    if re.search(
        r"\b(delivered|has arrived|was delivered|"
        r"received my (?:parcel|package|order)|"
        r"received the (?:parcel|package|order))\b",
        text
    ):
        return "DELIVERED"

    return "UNKNOWN"


def safe_delivery_match(new_ticket, historical_ticket):
    new_status = delivery_status(new_ticket)
    old_status = delivery_status(historical_ticket)

    # Reject when both statuses are known and conflict.
    if (
        new_status != "UNKNOWN"
        and old_status != "UNKNOWN"
        and new_status != old_status
    ):
        return False

    return True


if __name__ == "__main__":

    test_cases = [
        ("My order was delivered.", "My order was not delivered."),
        ("My order was not delivered.", "My order was delivered."),
        ("My package was delivered.", "My order was delivered."),
        ("Where is my order?", "Can you track my parcel?"),
        ("My package didn't arrive.", "My package was delivered."),
        ("I received my parcel.","My package was not delivered."),
        ("I haven't received my order.","My order was delivered."),
    ]

    for new_ticket, old_ticket in test_cases:
        result = safe_delivery_match(new_ticket, old_ticket)

        print("New ticket:", new_ticket)
        print("Historical:", old_ticket)
        print("Safe match:", result)
        print("-" * 40)
