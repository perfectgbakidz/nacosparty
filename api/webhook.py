from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from decimal import Decimal
import json

from schemas.webhook import FlutterwaveWebhookPayload
from crud.ticket import create_ticket
from core.config import FLW_SECRET_HASH
from core.crypto import encrypt_qr_payload
from utils.id_generator import generate_ticket_id
from database.session import SessionLocal
from models.ticket import Ticket

router = APIRouter(prefix="/api/webhook", tags=["Webhook"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/flutterwave")
async def flutterwave_webhook(
    request: Request,
    payload: FlutterwaveWebhookPayload,
    db: Session = Depends(get_db),
):
    signature = request.headers.get("verif-hash")
    if signature != FLW_SECRET_HASH:
        return {"status": "ignored_invalid_signature"}

    data = payload.data

    if str(data.status).lower() != "successful":
        return {"status": "ignored_not_successful"}

    # Idempotency check
    already_processed = (
        db.query(Ticket)
        .filter(Ticket.tx_ref.startswith(data.tx_ref))
        .first()
    )
    if already_processed:
        return {"status": "already_processed"}

    tickets_created = []

    # Parse attendees string
    attendees = []
    if data.meta and data.meta.attendees:
        try:
            attendees = json.loads(data.meta.attendees)
        except Exception:
            attendees = []

    # Fallback: if no attendees, create 1
    if not attendees:
        attendees = [{
            "full_name": data.customer.name,
            "gender": "N/A",
            "department": "N/A",
            "level": "N/A",
            "price": Decimal(data.amount),
            "email": data.customer.email,
            "phone": data.customer.phone_number or ""
        }]

    # Split total amount if price missing
    total_amount = Decimal(data.amount)
    split_price = total_amount / len(attendees)

    for attendee in attendees:
        ticket_id = generate_ticket_id()
        qr_data = encrypt_qr_payload(ticket_id)
        price = Decimal(attendee.get("price")) if attendee.get("price") else split_price
        stored_tx_ref = f"{data.tx_ref}-{ticket_id}"

        ticket = create_ticket(
            db,
            {
                "id": ticket_id,
                "tx_ref": stored_tx_ref,
                "full_name": attendee.get("full_name"),
                "email": attendee.get("email") or data.customer.email,
                "phone": attendee.get("phone") or data.customer.phone_number or "",
                "department": attendee.get("department") or "N/A",
                "level": attendee.get("level") or "N/A",
                "gender": attendee.get("gender") or "N/A",
                "price": price,
                "currency": data.currency,
                "payment_status": "successful",
                "qr_data": qr_data,
            },
        )

        tickets_created.append({
            "ticketId": ticket.id,
            "full_name": ticket.full_name,
        })

    db.commit()

    return {
        "status": "success",
        "tickets_created": len(tickets_created),
        "tickets": tickets_created,
    }
