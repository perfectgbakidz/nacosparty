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
# Create Tickets (POST /api/tickets)
# -----------------------------
@router.post("", response_model=List[TicketResponse])
def create_tickets(payload: TicketCreateRequest, db: Session = Depends(get_db)):
    tickets = []

    # Calculate split price if needed
    num_attendees = len(payload.attendees)
    try:
        total_amount = sum([Decimal(att.price) for att in payload.attendees if att.price])
    except:
        total_amount = Decimal("0")
    amount_per_attendee = total_amount / num_attendees if num_attendees else Decimal("0")

    for attendee in payload.attendees:
        ticket_id = generate_ticket_id()
        qr_data = encrypt_qr_payload(ticket_id)

        # Use attendee price if provided, else split amount
        try:
            price = Decimal(attendee.price)
        except:
            price = amount_per_attendee

        # Make tx_ref unique per ticket
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

    # Commit once
    db.commit()

    return tickets

    # Prevent duplicate tx_ref
    if get_ticket_by_tx_ref(db, payload.tx_ref):
        raise HTTPException(
            status_code=400,
            detail="Tickets already created for this transaction"
        )

    tickets = []

    for attendee in payload.attendees:
        ticket_id = generate_ticket_id()
        qr_data = encrypt_qr_payload(ticket_id)

        # Safe Decimal conversion
        try:
            price = Decimal(attendee.price)
        except:
            price = Decimal("0")

        ticket_data = {
            "id": ticket_id,
            "tx_ref": payload.tx_ref,
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

    return tickets

# -----------------------------
# Fetch all tickets (GET /api/tickets)
# -----------------------------
@router.get("", response_model=List[TicketResponse])
def fetch_tickets(db: Session = Depends(get_db), _: str = Depends(super_admin_required)):
    return get_all_tickets(db)

# -----------------------------
# Delete a ticket by ID (DELETE /api/tickets/{ticket_id})
# -----------------------------
@router.delete("/{ticket_id}")
def remove_ticket(ticket_id: str, db: Session = Depends(get_db), _: str = Depends(super_admin_required)):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    delete_ticket(db, ticket)
    return {"message": "Ticket deleted"}

# -----------------------------
# Check ticket availability (POST /api/tickets/check-availability)
# -----------------------------
@router.post("/check-availability", response_model=TicketAvailabilityResponse)
def check_ticket_availability(payload: TicketAvailabilityRequest, db: Session = Depends(get_db)):
    if get_ticket_by_email(db, payload.email):
        return {"available": False, "reason": "email_already_used"}

    if get_ticket_by_phone(db, payload.phone):
        return {"available": False, "reason": "phone_already_used"}

    return {"available": True}



