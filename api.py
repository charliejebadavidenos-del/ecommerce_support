
from fastapi import FastAPI,HTTPException

from pydantic import BaseModel, Field

from workflow import workflow

from storage import save_ticket
import json
import sqlite3


app = FastAPI(
    title="E-commerce Multi-Agent Support API",
    description="Backend for support ticket automation",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "E-commerce Support API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


class TicketRequest(BaseModel):
    ticket_text: str = Field(min_length=1)


@app.post("/ticket")
def create_ticket(ticket: TicketRequest):

    result = workflow.invoke({
        "ticket_text": ticket.ticket_text,
        "cleaned_text": "",
        "order_id": None
    })

    ticket_id = save_ticket(result)

    return {
        "message": "Ticket processed successfully",
        "ticket_id": ticket_id,
        "ticket_text": result["ticket_text"],
        "intent": result["intent"],
        "category": result["category"],
        "priority": result["priority"],
        "team": result["team"],
        "response": result["response"],
        "escalation_required": result["escalation_required"],
        "result": result
    }



@app.get("/ticket/{id}")
def get_ticket(id: str):

    conn = sqlite3.connect("support_tickets.db")

    try:
        row = conn.execute(
            """
            SELECT ticket_id, created_at, status, result_json
            FROM tickets
            WHERE ticket_id = ?
            """,
            (id,)
        ).fetchone()

    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return {
        "ticket_id": row[0],
        "created_at": row[1],
        "status": row[2],
        "result": json.loads(row[3])
    }


@app.post("/process")
def process_ticket(ticket: TicketRequest):

    result = workflow.invoke({
        "ticket_text": ticket.ticket_text,
        "cleaned_text": "",
        "order_id": None
    })

    return {
        "message": "Ticket processed without saving",
        "ticket_text": result["ticket_text"],
        "intent": result["intent"],
        "category": result["category"],
        "priority": result["priority"],
        "team": result["team"],
        "response": result["response"],
        "source_faq_id": result["source_faq_id"],
        "review_required": result["review_required"],
        "escalation_required": result["escalation_required"],
        "escalation_reasons": result["escalation_reasons"]
    }


##ADD Logs


@app.get("/logs/{id}")
def get_agent_logs(id: str):

    conn = sqlite3.connect("support_tickets.db")

    try:
        row = conn.execute(
            """
            SELECT result_json
            FROM tickets
            WHERE ticket_id = ?
            """,
            (id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    result = json.loads(row[0])

    return {
        "ticket_id": id,
        "logs": {
            "intake_agent": {
                "ticket_text": result.get("ticket_text"),
                "cleaned_text": result.get("cleaned_text"),
                "order_id": result.get("order_id")
            },
            "classification_agent": {
                "intent": result.get("intent"),
                "category": result.get("category"),
                "priority": result.get("priority"),
                "team": result.get("team")
            },
            "retrieval_agent": {
                "retrieved_faqs": result.get("retrieved_faqs")
            },
            "historical_resolution_agent": {
                "suggested_resolutions": result.get(
                    "suggested_resolutions", []
                )
            },
            "response_agent": {
                "response": result.get("response"),
                "source_faq_id": result.get("source_faq_id"),
                "review_required": result.get("review_required")
            },
            "escalation_agent": {
                "escalation_required": result.get(
                    "escalation_required"
                ),
                "escalation_reasons": result.get(
                    "escalation_reasons", []
                )
            }
        }
    }

