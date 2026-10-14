
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from agents.intake_agent import (
    clean_ticket,
    extract_order_id,
    extract_product,
    detect_intent,
    detect_sentiment,
)

from agents.classification_agent import classify_ticket, assign_priority
from agents.retrieval_agent import retrieve_faqs
from agents.response_agent import generate_response
from agents.escalation_agent import assess_escalation

from resolution_matcher import match_approved_resolutions
from semantic_resolution_matcher import match_semantic_resolutions

from storage import save_ticket

from pprint import pprint

# Data carried through the workflow
class TicketState(TypedDict):
    ticket_text: str
    cleaned_text: str
    order_id: str | None
    product: str | None
    intent: str
    category: str
    team: str
    priority: str
    retrieved_faqs: list[dict]
    response: str
    source_faq_id: str | None
    review_required: bool
    escalation_required: bool
    escalation_reasons: list[str]
    sentiment: str
    suggested_resolutions: list[dict]
   

# A node receives state and returns updates
def intake_node(state: TicketState) -> dict:
    cleaned_text = clean_ticket(state["ticket_text"])

    return {
        "cleaned_text": cleaned_text,
        "order_id": extract_order_id(cleaned_text),
        "product": extract_product(cleaned_text),
        "intent": detect_intent(cleaned_text),
        "sentiment": detect_sentiment(cleaned_text),       
    }

def classification_node(state: TicketState) -> dict:
    classification = classify_ticket(state["intent"])

    classification["priority"] = assign_priority(
        state["cleaned_text"],
        state["intent"],
    )

    return classification

def retrieval_node(state: TicketState) -> dict:
    return {
        "retrieved_faqs": retrieve_faqs(
            state["cleaned_text"],
            category=state["category"],
        )
    }

def response_node(state: TicketState) -> dict:
    return generate_response(
        state["order_id"],
        state["retrieved_faqs"],
        intent=state.get("intent"),
    )


def escalation_node(state: TicketState) -> dict:
    return assess_escalation(
        state["intent"],
        state["priority"],
        state["retrieved_faqs"],
        sentiment=state["sentiment"],
    )


def historical_resolution_node(state):
    matches = match_semantic_resolutions(
        ticket_text=state["ticket_text"],
        limit=3,
        min_similarity=0.30
    )

    return {
        "suggested_resolutions": matches
    }

# Build the workflow

builder = StateGraph(TicketState)

builder.add_node("intake", intake_node)
builder.add_node("classification", classification_node)
builder.add_node("retrieval", retrieval_node)
builder.add_node("response", response_node)
builder.add_node("escalation", escalation_node)
builder.add_node(
    "historical_resolution",
    historical_resolution_node
)

builder.add_edge(START, "intake")
builder.add_edge("intake", "classification")
builder.add_edge("classification", "retrieval")
builder.add_edge("retrieval", "historical_resolution")
builder.add_edge("historical_resolution", "response")
builder.add_edge("response", "escalation")
builder.add_edge("escalation", END)


workflow = builder.compile()

if __name__ == "__main__":
    ticket = input("Enter your support ticket: ")

    if not ticket.strip():
        print("Please enter a non-empty ticket.")
    else:
        result = workflow.invoke({
            "ticket_text": ticket,
            "cleaned_text": "",
            "order_id": None
        })

        ticket_id = save_ticket(result)

        print(f"\nSaved ticket ID: {ticket_id}")
        print("Status: pending_review")

        print("\nWorkflow result:")
        pprint(result, sort_dicts=False)