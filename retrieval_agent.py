import csv
import re
from pathlib import Path


FAQ_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "faq_knowledge_base_150_1.csv"
)

STOP_WORDS = {
    "a", "an", "the", "my", "i", "do", "how",
    "is", "are", "to", "of", "for", "please",
}



def get_keywords(text: str) -> set[str]:
    words = set(re.findall(r"\b\w+\b", text.casefold()))

    synonyms = {
        "replacement": "replace",
        "replaced": "replace",
        "replacing": "replace",
        "damaged": "defective",
        "broken": "defective",
        "faulty": "defective",
        "refund": "refunded",

        # Normalize wrong-item complaints
        "received": "receive",
        "receiving": "receive",
        "item": "product",
        
    }

    normalized_words = {
        synonyms.get(word, word)
        for word in words
        if word not in STOP_WORDS
    }

    return normalized_words



def retrieve_faqs(
    ticket_text: str,
    category: str | None = None,
    limit: int = 3,
) -> list[dict]:

    # Translate workflow categories to the labels used by the FAQ CSV.
    category_map = {
        "Delivery": "Delivery Issue",
        "Payment": "Payment Issue",
        "Refund": "Refund & Return",
        "Product Issue": "Product Issue",
    }

    # Preserve the existing safety behavior for unsupported categories.
    if category is not None and category not in category_map:
        return []

    faq_category = category_map.get(category)

    query_words = get_keywords(ticket_text)
    query_words -= {"was", "were", "have", "has", "been", "should", "what"}

    # Normalize common order-tracking questions.
    if "order" in query_words and (
        "where" in query_words
        or "status" in query_words
    ):
        query_words.add("track")

    # Normalize common refund-request questions.
    if "want" in query_words and "refunded" in query_words:
        query_words.add("request")

    # Order IDs do not help match general FAQ questions.
    query_words = {
        word for word in query_words
        if not re.fullmatch(r"ord\d+", word)
    }

    duplicate_charge_pattern = (
        r"\b(?:charged twice|paid twice|double charged|"
        r"double charge|duplicate charge|duplicate payment)\b"
    )


    duplicate_charge_query = bool(
        re.search(
            duplicate_charge_pattern,
            ticket_text,
            flags=re.IGNORECASE,
        )
    )

    matches = []

    with FAQ_PATH.open(encoding="utf-8-sig", newline="") as file:
        for faq in csv.DictReader(file):
            if faq_category and faq["category"] != faq_category:
                continue

            # A duplicate-charge query needs a FAQ on that subject.
            if duplicate_charge_query and not re.search(
                duplicate_charge_pattern,
                faq["question"],
                flags=re.IGNORECASE,
            ):
                continue

            question_words = get_keywords(faq["question"])

            shared_words = query_words & question_words

            # Intent-aware matching for replacement requests
            replacement_query = "replace" in query_words
            replacement_faq = "replace" in question_words

            intent_bonus = 0

            if replacement_query and replacement_faq:
                intent_bonus = 2


            # Match damaged, broken, or faulty products
            defective_query = "defective" in query_words
            defective_faq = "defective" in question_words

            if defective_query and defective_faq:
                intent_bonus = max(intent_bonus, 2)

 #Improve FAQ ranking
            score = len(shared_words) + intent_bonus

            # Penalize gift-specific FAQs for non-gift queries.
            gift_keywords = {"gift", "gifting", "recipient"}

            if (
                question_words & gift_keywords
                and not query_words & gift_keywords
            ):
                score -= 1

            if score < 2:
                continue


            matches.append({
                "faq_id": faq["faq_id"],
                "question": faq["question"],
                "answer": faq["answer"],
                "category": faq["category"],
                "matched_words": sorted(shared_words),
                "score": score,
            })

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:limit]


if __name__ == "__main__":
    query = input("Enter a question: ")
    results = retrieve_faqs(query)

    if not results:
        print("No keyword matches found.")
    else:
        for result in results:
            print(result)