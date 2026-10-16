"""Conservative hybrid FAQ retrieval with semantic relevance checks.

Replace the project-root hybrid_faq_retrieval.py with this file after backup.
"""
import csv
import re
from functools import lru_cache

from agents.retrieval_agent import FAQ_PATH, retrieve_faqs as keyword_retrieve

CATEGORY_MAP = {
    'Delivery': 'Delivery Issue',
    'Payment': 'Payment Issue',
    'Refund': 'Refund & Return',
    'Product Issue': 'Product Issue',
}
DUPLICATE_CHARGE = re.compile(
    r'\b(?:charged twice|paid twice|double charged|double charge|duplicate charge|duplicate payment)\b',
    re.I,
)


@lru_cache(maxsize=1)
def _semantic_index():
    import faiss
    from sentence_transformers import SentenceTransformer

    with FAQ_PATH.open(encoding='utf-8-sig', newline='') as handle:
        faqs = list(csv.DictReader(handle))
    model = SentenceTransformer('all-MiniLM-L6-v2')
    vectors = model.encode(
        [item['question'] for item in faqs],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype('float32')
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return model, index, faqs


def _semantic_candidates(text, category):
    model, index, faqs = _semantic_index()
    vector = model.encode(
        [text], convert_to_numpy=True, normalize_embeddings=True
    ).astype('float32')
    scores, indices = index.search(vector, len(faqs))
    target = CATEGORY_MAP.get(category)
    duplicate_query = bool(DUPLICATE_CHARGE.search(text))
    found = []
    for index_number, similarity in zip(indices[0], scores[0]):
        if index_number < 0:
            continue
        faq = faqs[int(index_number)]
        if target and faq['category'] != target:
            continue
        if duplicate_query and not DUPLICATE_CHARGE.search(faq['question']):
            continue
        found.append((faq, float(similarity)))
    return found


def retrieve_faqs(ticket_text: str, category: str | None = None, limit: int = 3) -> list[dict]:
    """Select a clear semantic winner, otherwise retain conservative keyword behavior."""
    if not ticket_text or not ticket_text.strip() or limit <= 0:
        return []
    if category is not None and category not in CATEGORY_MAP:
        return []

    keyword_matches = keyword_retrieve(ticket_text, category=category, limit=max(limit, 10))
    # Prefer tracking guidance when the customer explicitly asks to track an order.
    tracking_request = bool(
        re.search(r"\b(track|tracking)\b", ticket_text, re.I)
    )

    if category == "Delivery" and tracking_request:
        tracking_matches = [
            match for match in keyword_matches
            if match["faq_id"] == "FAQ001"
        ]

        if tracking_matches:
            return tracking_matches[:limit]
        
    duplicate_query = bool(DUPLICATE_CHARGE.search(ticket_text))
    if duplicate_query:
        # Do not answer a duplicate-charge complaint with an unrelated payment FAQ.
        keyword_matches = [
            match for match in keyword_matches
            if DUPLICATE_CHARGE.search(match.get('question', ''))
        ]

    try:
        semantic_matches = _semantic_candidates(ticket_text, category)
    except (ImportError, OSError, RuntimeError, ValueError):
        # Preserve the original keyword fallback when semantic services are unavailable.
        return keyword_matches[:limit]

    similarity_by_id = {faq['faq_id']: similarity for faq, similarity in semantic_matches}
    for match in keyword_matches:
        match['semantic_score'] = round(similarity_by_id.get(match['faq_id'], 0.0), 4)
        match['retrieval_method'] = 'hybrid'

    # A clear semantic match should not lose to unrelated keyword overlap.
    # Require both an absolute threshold and a margin over the next candidate.
    if semantic_matches:
        best_faq, best_score = semantic_matches[0]
        runner_up = semantic_matches[1][1] if len(semantic_matches) > 1 else 0.0
        if best_score >= 0.60 and best_score - runner_up >= 0.04:
            matching_keyword = next(
                (match for match in keyword_matches if match['faq_id'] == best_faq['faq_id']),
                None,
            )
            if matching_keyword is not None:
                return [matching_keyword]
            # Keep the stricter original fallback rule for FAQs without keyword evidence.
            if best_score >= 0.70 and best_score - runner_up >= 0.08:
                return [{
                    'faq_id': best_faq['faq_id'],
                    'question': best_faq['question'],
                    'answer': best_faq['answer'],
                    'category': best_faq['category'],
                    'matched_words': [],
                    'score': 2,
                    'semantic_score': round(best_score, 4),
                    'retrieval_method': 'semantic_fallback',
                }]

    if keyword_matches:
        # If multiple keyword matches are tied, downstream review safeguards apply.
        keyword_matches.sort(
            key=lambda match: (match['score'], match['semantic_score']), reverse=True
        )
        return keyword_matches[:limit]

    return []
