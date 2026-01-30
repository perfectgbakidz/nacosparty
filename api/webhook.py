from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from decimal import Decimal

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
    # 1️⃣ Verify webhook source
    signature = request.headers.get("verif-hash")
    if signature != FLW_SECRET_HASH:
        return {"status": "ignored"}

    data = payload.data

    # 2️⃣ Only successful payments
    if str(data.status).lower() != "successful":
        return {"status": "ignored"}

    # 3️⃣ Idempotency check (prevent duplicate processing)
    existing_ticket = (
        db.query(Ticket)
        .filter(Ticket.tx_ref.startswith(data.tx_ref))
        .first()
    )
    if existing_ticket:
        return {"status": "already_processed"}

    tickets_created = []

    # 4️⃣ Get attendees
    attendees = data.meta.attendees if data.meta and data.meta.attendees else []

    if not attendees:
        attendees = [{
            "full_name": data.customer.name,
            "gender": "N/A",
            "department": "N/A",
            "level": "N/A",
            "price": data.amount
        }]

    # 5️⃣ Create tickets
    for attendee in attendees:
        ticket_id = generate_ticket_id()
        qr_data = encrypt_qr_payload(ticket_id)

        # 🔥 IMPORTANT: tx_ref stored = original + ticket ID
        stored_tx_ref = f"{data.tx_ref}-{ticket_id}"

        ticket = create_ticket(
            db,
            {
                "id": ticket_id,
                "tx_ref": stored_tx_ref,
                "full_name": attendee.get("full_name"),
                "email": data.customer.email,
                "phone": data.customer.phone_number or "",
                "department": attendee.get("department"),
                "level": attendee.get("level"),
                "gender": attendee.get("gender"),
                "price": Decimal(attendee.get("price")),
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

    return {"status": "success", "tickets": tickets_created}
