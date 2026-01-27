from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from schemas.ticket import TicketResponse, TicketAvailabilityRequest, TicketAvailabilityResponse
from crud.ticket import get_all_tickets, delete_ticket, get_ticket_by_id, get_ticket_by_email, get_ticket_by_phone
from core.dependencies import super_admin_required
from database.session import SessionLocal



router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=List[TicketResponse])
def fetch_tickets(
    db: Session = Depends(get_db),
    _: str = Depends(super_admin_required)
):
    return get_all_tickets(db)


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
    return {"message": "Ticket deleted"}


@router.post(
    "/check-availability",
    response_model=TicketAvailabilityResponse
)
def check_ticket_availability(
    payload: TicketAvailabilityRequest,
    db: Session = Depends(get_db)
):
    if get_ticket_by_email(db, payload.email):
        return {
            "available": False,
            "reason": "email_already_used"
        }

    if get_ticket_by_phone(db, payload.phone):
        return {
            "available": False,
            "reason": "phone_already_used"
        }

    return {"available": True}