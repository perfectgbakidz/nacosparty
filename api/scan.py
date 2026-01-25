from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.scan import ScanRequest, ScanResponse
from crud.ticket import get_ticket_by_id, mark_ticket_checked_in
from core.crypto import decrypt_qr_payload
from core.dependencies import super_admin_required
from database.session import SessionLocal

router = APIRouter(prefix="/api/scan", tags=["Scan"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=ScanResponse)
def scan_ticket(
    payload: ScanRequest,
    db: Session = Depends(get_db),
    _: str = Depends(super_admin_required)
):
    try:
        ticket_id = decrypt_qr_payload(payload.qr_data)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid QR code")

    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.is_checked_in:
        return {
            "ticketId": ticket.id,
            "fullName": ticket.full_name,
            "checkedIn": True,
            "message": "Ticket already used"
        }

    ticket = mark_ticket_checked_in(db, ticket)

    return {
        "ticketId": ticket.id,
        "fullName": ticket.full_name,
        "checkedIn": True,
        "message": "Check-in successful"
    }
