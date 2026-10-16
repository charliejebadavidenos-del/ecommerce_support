
from functools import lru_cache

from transformers import pipeline

from agents.intake_agent import detect_sentiment


MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"


@lru_cache(maxsize=1)
def load_sentiment_model():
    return pipeline(
        task="text-classification",
        model=MODEL_NAME,
        device=-1
    )


def predict_sentiment(ticket_text: str) -> dict:
    text = ticket_text.strip()

    if not text:
        return {
            "sentiment": "neutral",
            "sentiment_confidence": 0.0,
            "sentiment_source": "empty_input"
        }

    try:
        result = load_sentiment_model()(text, truncation=True)[0]

        return {
            "sentiment": result["label"].lower(),
            "sentiment_confidence": round(
                float(result["score"]), 4
            ),
            "sentiment_source": "roberta"
        }

    except Exception:
        # Preserve the existing rule-based behavior if
        # the pretrained model cannot be loaded or executed.
        return {
            "sentiment": detect_sentiment(text),
            "sentiment_confidence": None,
            "sentiment_source": "rule_based_fallback"
        }
