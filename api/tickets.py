from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from schemas.ticket import (
    TicketResponse,
    TicketAvailabilityRequest,
    TicketAvailabilityResponse
)

from crud.ticket import (
    get_all_tickets,
    get_ticket_by_id,
    get_ticket_by_email,
    get_ticket_by_phone,
    delete_ticket
)

from core.dependencies import super_admin_required
from database.session import SessionLocal
from models.ticket import Ticket

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


# --------------------------------------------------
# FETCH TICKETS BY TRANSACTION REFERENCE (FRONTEND)
# GET /api/tickets?tx_ref=TX-12345
# --------------------------------------------------
@router.get("", response_model=List[TicketResponse])
def fetch_tickets_by_tx_ref(
    tx_ref: str = Query(..., description="Original transaction reference"),
    db: Session = Depends(get_db),
):
    tickets = (
        db.query(Ticket)
        .filter(Ticket.tx_ref.startswith(tx_ref))
        .all()
    )

    if not tickets:
        raise HTTPException(status_code=404, detail="Tickets not found")

    return tickets


# --------------------------------------------------
# ADMIN: Fetch ALL tickets
# GET /api/tickets/admin/all
# --------------------------------------------------
@router.get("/admin/all", response_model=List[TicketResponse])
def fetch_all_tickets_admin(
    db: Session = Depends(get_db),
    _: str = Depends(super_admin_required),
):
    return get_all_tickets(db)


# --------------------------------------------------
# ADMIN: Delete ticket by ID
# DELETE /api/tickets/{ticket_id}
# --------------------------------------------------
@router.delete("/{ticket_id}")
def remove_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(super_admin_required),
):
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    delete_ticket(db, ticket)
    db.commit()
    return {"message": "Ticket deleted"}


# --------------------------------------------------
# Check ticket availability (optional)
# --------------------------------------------------
@router.post("/check-availability", response_model=TicketAvailabilityResponse)
def check_ticket_availability(
    payload: TicketAvailabilityRequest,
    db: Session = Depends(get_db),
):
    if get_ticket_by_email(db, payload.email):
        return {"available": False, "reason": "email_already_used"}

    if get_ticket_by_phone(db, payload.phone):
        return {"available": False, "reason": "phone_already_used"}

    return {"available": True}
