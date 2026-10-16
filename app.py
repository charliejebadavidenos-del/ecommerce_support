import logging
import sqlite3
from contextlib import closing
import requests
import streamlit as st

from workflow import workflow
from learning_agent import initialize_learning_feedback, record_retrieval_feedback
from storage import DB_PATH

from storage import (
    save_ticket,
    load_tickets,
    resolve_ticket,
    load_resolution,
    approve_resolution,
)

def existing_feedback(query_ticket_id: str, historical_ticket_id: str) -> str | None:
    """Prevent repeated votes for the same ticket/suggestion pair."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        row = connection.execute(
            """SELECT feedback FROM retrieval_feedback
               WHERE query_ticket_id = ? AND historical_ticket_id = ?
               ORDER BY feedback_id DESC LIMIT 1""",
            (query_ticket_id, historical_ticket_id),
        ).fetchone()
    return row[0] if row else None


st.set_page_config(
    page_title="E-commerce Support",
    page_icon="🎫",
    layout="wide",
)

st.title("E-commerce Support")
st.caption("Submit a ticket to generate a response draft for review.")

with st.form("ticket_form"):
    ticket_text = st.text_area(
        "Customer support ticket",
        placeholder="Please track my order ORD12345",
        height=150,
    )

    submitted = st.form_submit_button("Process and save ticket")


if submitted:
    st.session_state.pop("latest_ticket", None)

    if not ticket_text.strip():
        st.warning("Please enter a ticket before submitting.")
    else:
        try:
            with st.spinner("Processing ticket..."):

                api_response = requests.post(
                    "http://127.0.0.1:8000/ticket",
                    json={"ticket_text": ticket_text},
                    timeout=120
                )

                api_response.raise_for_status()

                api_data = api_response.json()

                ticket_id = api_data["ticket_id"]
                result = api_data["result"]



            st.session_state["latest_ticket"] = {
                "ticket_id": ticket_id,
                "result": result,
            }
            st.session_state["history_ticket_selector"] = ticket_id
        except Exception:
            logging.exception("Ticket processing or saving failed")
            st.error(
                "The ticket could not be processed or saved. "
                "Check the terminal for details."
            )


if "latest_ticket" in st.session_state:
    
    saved = st.session_state["latest_ticket"]
    result = saved["result"]

    st.success("New ticket saved. See Ticket history for its current status.")
    st.caption(f"Ticket ID: {saved['ticket_id']}")

    st.subheader("Submitted ticket")
    st.write(result["ticket_text"])

    category_col, priority_col, team_col = st.columns(3)
    category_col.metric("Category", result["category"])
    priority_col.metric("Priority", result["priority"])
    team_col.metric("Assigned team", result["team"])

    st.write("Order ID:", result["order_id"] or "Not provided")
    st.write("Product:", result.get("product") or "Not identified")
    st.write("Detected intent:", result["intent"])
    st.write("Sentiment:", result.get("sentiment", "Not recorded"))

#Response and escalation
    st.subheader("Response draft")
    st.write(result["response"])
    st.caption(
        f"Source FAQ: {result['source_faq_id'] or 'None'}"
    )

    if result["review_required"]:
        st.info("Human review required. This response has not been sent.")

    if result["escalation_required"]:
        st.warning("Flagged for escalation")
        for reason in result["escalation_reasons"]:
            st.write(f"• {reason}")
    else:
        st.write("No escalation rule triggered.")

##Retrieved FAQ candidates

    with st.expander("Retrieved FAQ candidates"):
        if result["retrieved_faqs"]:
            st.dataframe(result["retrieved_faqs"])
        else:
            st.write("No matching FAQ found.")

## Historical resolutions and human feedback

    st.subheader("Suggested Historical Resolutions")
    suggestions = result.get("suggested_resolutions", [])
    query_ticket_id = saved["ticket_id"]

    if suggestions:
        try:
            initialize_learning_feedback()
        except Exception:
            logging.exception("Feedback table initialization failed")
            st.error("Feedback storage is unavailable. Existing suggestions remain viewable.")
        else:
            for item in suggestions:
                historical_id = item["ticket_id"]
                with st.expander(
                    f"Ticket {historical_id} - Similarity: {item['similarity']:.0%}"
                ):
                    st.write("**Previous customer issue:**", item["original_ticket"])
                    st.write("**Approved resolution:**", item["resolution"])
                    st.caption(
                        f"Learning score: {item.get('learning_score', item['similarity']):.4f}"
                    )
                    st.info("For human review only. Do not automatically send this resolution.")
                    try:
                        prior_vote = existing_feedback(query_ticket_id, historical_id)
                    except Exception:
                        logging.exception("Unable to read retrieval feedback")
                        st.error("Unable to check existing feedback.")
                        continue
                    if prior_vote:
                        st.success(f"Feedback already recorded: {prior_vote.replace('_', ' ').title()}")
                    else:
                        helpful_col, unhelpful_col = st.columns(2)
                        for col, feedback, label in (
                            (helpful_col, "helpful", "👍 Helpful"),
                            (unhelpful_col, "not_helpful", "👎 Not Helpful"),
                        ):
                            if col.button(
                                label,
                                key=f"feedback_{query_ticket_id}_{historical_id}_{feedback}",
                            ):
                                try:
                                    record_retrieval_feedback(
                                        query_ticket_id, historical_id, feedback
                                    )
                                except (ValueError, sqlite3.Error) as error:
                                    st.error(f"Could not save feedback: {error}")
                                except Exception:
                                    logging.exception("Unexpected feedback recording error")
                                    st.error("Could not save feedback. Check the terminal.")
                                else:
                                    st.rerun()
    else:
        st.info("No matching approved historical resolutions found.")


##Ticket History

st.divider()
st.subheader("Ticket history")
st.caption("Latest 100 saved tickets. Timestamps are in UTC.")

tickets = load_tickets()

if not tickets:
    st.info("No saved tickets yet.")
else:
    history_rows = [
        {
            "Ticket ID": ticket["ticket_id"],
            "Created": ticket["created_at"],
            "Status": ticket["status"],
            "Category": ticket["result"].get("category", ""),
            "Priority": ticket["result"].get("priority", ""),
            "Customer message": ticket["result"]["ticket_text"],
        }
        for ticket in tickets
    ]

    st.dataframe(history_rows, hide_index=True)

    tickets_by_id = {
        ticket["ticket_id"]: ticket
        for ticket in tickets
    }


    def ticket_label(ticket_id):
        ticket = tickets_by_id[ticket_id]
        message = ticket["result"]["ticket_text"]
        return f"{ticket_id[:8]} | {message[:70]}"


    selected_id = st.selectbox(
        "Choose an existing ticket to review or view its resolution",
        options=list(tickets_by_id),
        format_func=ticket_label,
        key="history_ticket_selector",
    )

    selected_ticket = tickets_by_id[selected_id]

    with st.expander("View saved ticket details"):
        st.json(selected_ticket)


## Resolution

if tickets:
    st.subheader("Human review")
    st.caption(f"Reviewing ticket: {selected_id}")
    st.write("Current status:", selected_ticket["status"])

    if selected_ticket["status"] == "resolved":
        st.success("This ticket has already been resolved.")

        saved_resolution = load_resolution(selected_id)

        if saved_resolution:
            st.write("Saved resolution:")
            st.write(saved_resolution["resolution"])
            st.caption(
                f"Resolved at: {saved_resolution['resolved_at']} UTC"
            )
            
            approval_status = saved_resolution.get(
                "approval_status", "pending"
            )

            st.write("Approval status:", approval_status)

            if approval_status == "pending":
                if st.button(
                    "Approve Resolution",
                    key=f"approve_{selected_id}"
                ):
                    try:
                        approve_resolution(selected_id)
                    except ValueError as error:
                        st.warning(str(error))
                    except Exception:
                        logging.exception("Resolution approval failed")
                        st.error("Unable to approve the resolution.")
                    else:
                        st.success("Resolution approved successfully.")
                        st.rerun()

        else:
            st.warning("No resolution record was found for this ticket.")
    else:
        with st.form(f"review_{selected_id}"):
            resolution = st.text_area(
                "Actual resolution",
                placeholder="Describe the action taken and verified outcome.",
                key=f"resolution_{selected_id}",
            )

            confirmed = st.checkbox(
                "I confirm that this issue has been resolved.",
                key=f"confirmed_{selected_id}",
            )

            resolve_submitted = st.form_submit_button(
                "Save resolution and Mark resolved"
            )

        if resolve_submitted:
            if not resolution.strip():
                st.warning("Please enter the actual resolution.")
            elif not confirmed:
                st.warning("Confirm resolution before closing the ticket.")
            else:
                try:
                    resolve_ticket(selected_id, resolution)
                except ValueError as error:
                    st.warning(str(error))
                except Exception:
                    logging.exception("Failed to save resolution")
                    st.error(
                        "The resolution could not be saved. "
                        "Check the terminal for details."
                    )
                else:
                    # Remove the old pending-review display.
                    st.session_state.pop("latest_ticket", None)
                    st.rerun()