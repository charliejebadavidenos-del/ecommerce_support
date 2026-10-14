

import re

from storage import load_approved_resolutions


def tokenize(text: str) -> set[str]:
    stop_words = {
        "a", "an", "the", "is", "are",
        "my", "i", "me", "where", "what",
        "how", "do", "does", "for", "to",
        "of", "please",
    }

    synonyms = {
        "package": "order",
        "parcel": "order",
        "damaged": "broken",
        "defective": "broken",
    }

    words = re.findall(r"\b[a-z0-9]+\b", text.lower())

    return {
        synonyms.get(word, word)
        for word in words
        if word not in stop_words
    }



def has_negation(text: str) -> bool:
    text = text.lower().replace("’", "'")

    negative_words = {
        "not", "no", "never",
        "cannot", "without",
    }

    words = set(re.findall(r"\b[a-z0-9]+\b", text))

    has_negative_word = bool(words & negative_words)

    has_contraction = bool(
        re.search(r"\b[a-z]+n't\b", text)
    )

    return has_negative_word or has_contraction



def match_approved_resolutions(
    ticket_text: str,
    limit: int = 3,
    min_similarity: float = 0.5,
) -> list[dict]:

    approved = load_approved_resolutions()
    query_words = tokenize(ticket_text)

    matches = []

    
    for item in approved:
        previous_ticket = item["original_ticket"]

        if has_negation(ticket_text) != has_negation(previous_ticket):
            continue

        previous_words = tokenize(previous_ticket)


        union = query_words | previous_words

        if not union:
            continue

        intersection = query_words & previous_words
        similarity = len(intersection) / len(union)

        if similarity >= min_similarity:
            matches.append({
                **item,
                "similarity": round(similarity, 3),
            })

    matches.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )

    return matches[:limit]
