def assess_escalation(
    intent: str,
    priority: str,
    faqs: list[dict],
    sentiment: str = "neutral",
) -> dict:
    reasons = []

    if sentiment == "negative":
        reasons.append("Negative sentiment requires human review")

    if priority == "High":
        reasons.append("High-priority ticket")

    if intent in {"unknown", "multiple_intents"}:
        reasons.append("Intent requires clarification")

    if not faqs:
        reasons.append("No matching FAQ found")
    elif len(faqs) > 1:
        if faqs[0]["score"] == faqs[1]["score"]:
            reasons.append("Top FAQ candidates have equal scores")

    return {
        "escalation_required": bool(reasons),
        "escalation_reasons": reasons,
    }