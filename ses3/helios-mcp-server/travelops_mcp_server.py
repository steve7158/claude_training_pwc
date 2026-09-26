from mcp.server.fastmcp import FastMCP

mcp = FastMCP("travelops")

BOOKINGS = {
    "BK-1001": {
        "customer": "Maya Rao",
        "route": "DEL-LIS",
        "fare": "economy",
        "status": "confirmed",
        "amount_inr": 72000,
        "departure": "2026-07-20",
        "baggage": "1 cabin bag + 1 checked bag up to 23 kg",
    },
    "BK-1002": {
        "customer": "Arjun Mehta",
        "route": "DEL-LIS",
        "fare": "economy",
        "status": "cancelled_by_airline",
        "amount_inr": 86000,
        "departure": "2026-07-21",
        "baggage": "1 cabin bag + 1 checked bag up to 23 kg",
    },
}

REFUND_POLICY = """
Helios Refund Policy v3
- Airline-cancelled trips are eligible for full refund.
- Customer-requested cancellations may include fare-rule charges.
- Refunds above INR 50,000 require human approval.
- Medical emergency, legal threat, chargeback, compensation demand, or unclear identity must be escalated.
- The support AI may estimate a refund but must not issue money without approval.
""".strip()


@mcp.tool()
def get_booking(booking_id: str) -> dict:
    """
    Look up one booking by booking ID. Read-only.
    Use this before refund or customer response decisions.
    Does not modify booking state and does not expose payment card details.
    """
    booking = BOOKINGS.get(booking_id)
    if not booking:
        return {"ok": False, "error_type": "BOOKING_NOT_FOUND", "booking_id": booking_id}
    return {"ok": True, "booking": booking}


@mcp.tool()
def estimate_refund(booking_id: str, reason: str) -> dict:
    """
    Estimate refund amount for one booking. Calculation-only, not a payment action.
    Use only after get_booking confirms the booking exists.
    Returns approval_required=true when refund amount crosses policy threshold.
    """
    booking = BOOKINGS.get(booking_id)
    if not booking:
        return {"ok": False, "error_type": "BOOKING_NOT_FOUND", "booking_id": booking_id}
    if booking["status"] == "cancelled_by_airline":
        amount = booking["amount_inr"]
        return {
            "ok": True,
            "booking_id": booking_id,
            "refund_amount_inr": amount,
            "approval_required": amount > 50000,
            "reason": reason,
        }
    return {
        "ok": True,
        "booking_id": booking_id,
        "refund_amount_inr": int(booking["amount_inr"] * 0.70),
        "approval_required": True,
        "reason": "Customer cancellation requires human review.",
    }


@mcp.tool()
def check_escalation(ticket_text: str, amount_inr: int | None = None) -> dict:
    """
    Check whether a ticket must be escalated to a human.
    Read-only risk classification. Does not contact the customer and does not change state.
    """
    text = ticket_text.lower()
    risky_terms = ["oxygen", "medical", "legal", "lawyer", "compensation", "chargeback", "stranded"]
    reasons = [term for term in risky_terms if term in text]
    if amount_inr is not None and amount_inr > 50000:
        reasons.append("refund_above_50000")
    return {"escalate": bool(reasons), "reasons": reasons}


@mcp.tool()
def create_receipt_draft(booking_id: str, refund_amount_inr: int | None = None) -> dict:
    """
    Create a receipt email draft for one booking. Does not send email.
    Use only after get_booking confirms the booking exists.
    """
    booking = BOOKINGS.get(booking_id)
    if not booking:
        return {"ok": False, "error_type": "BOOKING_NOT_FOUND", "booking_id": booking_id}
    return {
        "ok": True,
        "to_customer": booking["customer"],
        "subject": f"Receipt draft for booking {booking_id}",
        "body": f"Dear {booking['customer']}, this is a draft receipt for booking {booking_id}. Refund estimate: {refund_amount_inr}.",
        "sent": False,
    }


@mcp.resource("travelops://policy/refund")
def refund_policy() -> str:
    """Return the current Helios Travel refund and escalation policy."""
    return REFUND_POLICY


@mcp.prompt()
def triage_travel_ticket(ticket_text: str) -> str:
    """Reusable triage prompt for Helios Travel support tickets."""
    return f"""
You are a Helios Travel support triage assistant.
Use the connected travelops MCP tools when booking, refund, or escalation facts are needed.
Return:
1. Customer intent
2. Tools/resources to use
3. Escalation decision
4. Customer-safe response draft

Ticket:
{ticket_text}
""".strip()


if __name__ == "__main__":
    mcp.run()
