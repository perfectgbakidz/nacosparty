from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from schemas.ticket import (
    TicketResponse,
    TicketCreateRequest,
    TicketAvailabilityRequest,
    TicketAvailabilityResponse
)
from crud.ticket import (
    create_ticket,
    get_all_tickets,
    get_ticket_by_id,
    get_ticket_by_email,
    get_ticket_by_phone,
    get_ticket_by_tx_ref,
    delete_ticket
)
from core.dependencies import super_admin_required
from core.crypto import encrypt_qr_payload
from utils.id_generator import generate_ticket_id
from database.session import SessionLocal

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


# -----------------------------
# Database dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Create Tickets (ADMIN / MANUAL USE ONLY)
# -----------------------------
@router.post("", response_model=List[TicketResponse])
def create_tickets(payload: TicketCreateRequest, db: Session = Depends(get_db)):
    """
    ⚠️ This endpoint should NOT be called by the frontend after payment.
    Tickets are normally created via Flutterwave webhook.

    This is kept for admin/manual creation and is idempotent.
    """

    # 🔒 Prevent duplicate tickets for same transaction
    existing_tickets = get_ticket_by_tx_ref(db, payload.tx_ref)
    if existing_tickets:
        return existing_tickets

    tickets: List = []

    num_attendees = len(payload.attendees)
    total_amount = sum([Decimal(att.price) for att in payload.attendees])
    amount_per_attendee = total_amount / num_attendees if num_attendees else Decimal("0")

    for attendee in payload.attendees:
        ticket_id = generate_ticket_id()
        qr_data = encrypt_qr_payload(ticket_id)

        price = Decimal(attendee.price) if attendee.price else amount_per_attendee

        # IMPORTANT: mix original tx_ref with ticket id
        unique_tx_ref = f"{payload.tx_ref}-{ticket_id}"

        ticket_data = {
            "id": ticket_id,
            "tx_ref": unique_tx_ref,
            "full_name": attendee.full_name,
            "email": payload.email,
            "phone": payload.phone,
            "department": attendee.department,
            "level": attendee.level,
            "gender": attendee.gender,
            "price": price,
            "currency": "NGN",
            "payment_status": "successful",
            "qr_data": qr_data,
        }

        ticket = create_ticket(db, ticket_data)
        tickets.append(ticket)

    db.commit()
    return tickets


# -----------------------------
# Fetch tickets by ORIGINAL tx_ref (PUBLIC)
# -----------------------------
@router.get("/by-tx-ref", response_model=List[TicketResponse])
def fetch_tickets_by_tx_ref(tx_ref: str, db: Session = Depends(get_db)):
    """
    Used by frontend after successful payment.
    Returns ALL tickets created from the same transaction.
    """
    return get_ticket_by_tx_ref(db, tx_ref)


# -----------------------------
# Fetch all tickets (ADMIN ONLY)
# -----------------------------
@router.get("", response_model=List[TicketResponse])
def fetch_all_tickets(
    db: Session = Depends(get_db),
    _: str = Depends(super_admin_required)
):
    return get_all_tickets(db)


# -----------------------------
# Delete a ticket (ADMIN ONLY)
# -----------------------------
@router.delete("/{ticket_id}")
def remove_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(super_admin_required)
):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    delete_ticket(db, ticket)
    db.commit()
    return {"message": "Ticket deleted"}


# -----------------------------
# Check ticket availability
# -----------------------------
@router.post("/check-availability", response_model=TicketAvailabilityResponse)
def check_ticket_availability(
    payload: TicketAvailabilityRequest,
    db: Session = Depends(get_db)
):
    if get_ticket_by_email(db, payload.email):
        return {"available": False, "reason": "email_already_used"}

    if get_ticket_by_phone(db, payload.phone):
        return {"available": False, "reason": "phone_already_used"}

    return {"available": True}
