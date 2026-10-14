# ecommerce_support
 Build an AI-powered multi-agent system that can automatically understand, classify, respond, and route tickets, reducing human effort while improving resolution quality and speed.

# E-commerce Multi-Agent Support Ticket Automation System

**Status:** Tested prototype; not production-ready.  **Handover date:** 2026-10-14.

## What it does
Intake → classification → FAQ retrieval → historical approved-resolution matching → response draft → escalation → human review, with SQLite persistence and a Streamlit UI.

## Start locally (Windows CMD)
```bat
cd /d D:\AI_Projects\ecommerce_support
.venv314\Scripts\activate
streamlit run app.py --server.fileWatcherType none
```
## Project files
`app.py`, `workflow.py`, `agents/`, `semantic_resolution_matcher.py`, `storage.py`, `data/faq_knowledge_base_150_1.csv`, `support_tickets.db`.
