from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

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
    # -----------------------
    # Verify signature
    # -----------------------
    signature = request.headers.get("verif-hash")
    if signature != FLW_SECRET_HASH:
        return {"status": "ignored"}

    data = payload.data

    # -----------------------
    # Only process successful payments
    # -----------------------
    if data.status != "successful":
        return {"status": "ignored"}

    # -----------------------
    # Process all attendees
    # -----------------------
    attendees = data.meta.attendees if data.meta else []

    tickets_created = []

    for attendee in attendees:
        ticket_id = generate_ticket_id()
        qr_data = encrypt_qr_payload(ticket_id)

        ticket = create_ticket(
            db,
            {
                "id": ticket_id,
                "tx_ref": data.tx_ref,
                "full_name": attendee.full_name,
                "email": data.customer.email,
                "phone": data.customer.phone_number or "",
                "department": attendee.department,
                "level": attendee.level,
                "gender": attendee.gender,
                "price": attendee.price,
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

    db.commit()

    return {
        "status": "success",
        "tickets": tickets_created
    }
