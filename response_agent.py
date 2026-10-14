def generate_response(
    order_id: str | None,
    faqs: list[dict],
    intent: str | None = None,
) -> dict:
    order_reference = (
        f" regarding order {order_id}" if order_id else ""
    )


    if intent == "delivery_status" and not faqs:
        return {
            "response": (
                f"Thank you for contacting us{order_reference}. "
                "Could you please provide your order ID and confirm "
                "whether the tracking status shows 'Delivered' "
                "or 'In Transit'?"
            ),
            "source_faq_id": None,
            "review_required": True,
        }


    if intent == "payment_problem" and not faqs:
        return {
            "response": (
                f"Thank you for contacting us{order_reference}. "
                "We understand you may have been charged more than once. "
                "Please provide your order ID and the relevant "
                "payment transaction reference numbers so our "
                "Payment Support team can investigate. "
                "Do not share your card number, CVV, or OTP."
            ),
            "source_faq_id": None,
            "review_required": True,
        }


    if not faqs:
        return {
            "response": (
                f"Thank you for contacting us{order_reference}. "
                "We couldn't find matching guidance in our FAQ. "
                "Could you provide more details about the issue?"
            ),
            "source_faq_id": None,
            "review_required": True,
        }

    if len(faqs) > 1 and faqs[0]["score"] == faqs[1]["score"]:
        return {
            "response": (
                f"Thank you for contacting us{order_reference}. "
                "Your request needs a support specialist's review "
                "to determine the appropriate next step."
            ),
            "source_faq_id": None,
            "review_required": True,
        }


    selected_faq = faqs[0]

    return {
        "response": (
            f"Thank you for contacting us{order_reference}. "
            f"{selected_faq['answer']}"
        ),
        "source_faq_id": selected_faq["faq_id"],
        "review_required": True,
    }