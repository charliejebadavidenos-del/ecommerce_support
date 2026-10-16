"""Context-aware, FAQ-grounded customer support response drafts.

Responses are always drafts for human review; no external order/payment actions
are performed and no account or order status is inferred.
"""


def generate_response(
    order_id: str | None,
    faqs: list[dict],
    intent: str | None = None,
    sentiment: str = "neutral",
) -> dict:
    reference = f" regarding order {order_id}" if order_id else ""
    if (sentiment or "").lower() == "negative":
        opening = f"I'm sorry you're experiencing this issue{reference}. "
    else:
        opening = f"Thank you for contacting us{reference}. "

    def draft(message: str, faq_id: str | None = None) -> dict:
        return {
            "response": opening + message,
            "source_faq_id": faq_id,
            "review_required": True,
        }

    if not faqs:
        if intent == "delivery_status":
            if order_id:
                return draft(
                    "Please check the latest tracking information under My Orders > "
                    "Track Package. If the status is unclear, our delivery support "
                    "team can review it. We have not independently verified the "
                    "delivery status."
                )
            return draft(
                "Could you please provide your order ID and confirm whether "
                "the tracking page shows 'Delivered' or 'In Transit'? "
                "Please do not share account passwords or OTPs."
            )
        if intent == "payment_problem":
            return draft(
                "Our Payment Support team can investigate a possible duplicate "
                "charge. Please provide your order ID and relevant transaction "
                "reference numbers through the secure support channel. "
                "Do not share card numbers, CVV, PIN or OTP."
            )
        return draft(
            "We couldn't find sufficiently clear FAQ guidance for this request. "
            "Could you provide a little more detail so a support specialist "
            "can review the appropriate next steps?"
        )

    # Preserve the existing ambiguity rule used by the working application.
    if len(faqs) > 1 and faqs[0].get("score") == faqs[1].get("score"):
        return draft(
            "Your request needs a support specialist's review to determine "
            "the appropriate next step."
        )

    selected = faqs[0]
    answer = str(selected.get("answer") or "").strip()
    if not answer:
        return draft(
            "A support specialist will review your request because the "
            "retrieved FAQ does not contain usable guidance."
        )

    # The answer is sourced from the maintained FAQ knowledge base. Do not
    # invent an order status, approved refund, or completed action.
    return draft(answer, selected.get("faq_id"))
