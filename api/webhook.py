from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from decimal import Decimal

from schemas.webhook import FlutterwaveWebhookPayload
from crud.ticket import create_ticket, get_ticket_by_tx_ref
from core.config import FLW_SECRET_HASH
from core.crypto import encrypt_qr_payload
from utils.id_generator import generate_ticket_id
from database.session import SessionLocal

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
    # Verify Flutterwave webhook
    signature = request.headers.get("verif-hash")
    if signature != FLW_SECRET_HASH:
        return {"status": "ignored"}

    data = payload.data

    # Only process successful payments
    if data.status.lower() != "successful":
        return {"status": "ignored"}

    # Prevent duplicate processing
    if get_ticket_by_tx_ref(db, str(data.tx_ref)):
        return {"status": "already_processed"}

    tickets_created = []

    # Safe handling if no attendees sent
    attendees = data.meta.attendees if (data.meta and data.meta.attendees) else []

    # If frontend sent no attendees, create a single ticket with customer info
    if not attendees:
        attendees = [
            {
                "full_name": data.customer.name,
                "gender": "N/A",
                "department": "NACOS",
                "level": "N/A",
                "price": Decimal(data.amount)
            }
        ]

    for attendee in attendees:
        ticket_id = generate_ticket_id()
        qr_data = encrypt_qr_payload(ticket_id)

        # Ensure price is Decimal
        price = Decimal(attendee.price) if attendee.price else Decimal(data.amount)

        ticket = create_ticket(
            db,
            {
                "id": ticket_id,
                "tx_ref": str(data.tx_ref),
                "full_name": attendee.full_name,
                "email": data.customer.email,
                "phone": data.customer.phone_number or "",
                "department": attendee.department,
                "level": attendee.level,
                "gender": attendee.gender,
                "price": price,
                "currency": data.currency,
                "payment_status": data.status,
                "qr_data": qr_data,
            },
        )

        tickets_created.append({
            "ticketId": ticket.id,
            "qrData": qr_data,
            "full_name": ticket.full_name
        })

    # Commit once after all tickets
    db.commit()

    return {
        "status": "success",
        "tickets": tickets_created
    }
