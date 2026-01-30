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


# -----------------------------
# Database Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Flutterwave Webhook
# -----------------------------
@router.post("/flutterwave")
async def flutterwave_webhook(
    request: Request,
    payload: FlutterwaveWebhookPayload,
    db: Session = Depends(get_db),
):
    # 1️⃣ Verify webhook source
    signature = request.headers.get("verif-hash")
    if signature != FLW_SECRET_HASH:
        return {"status": "ignored_invalid_signature"}

    data = payload.data

    # 2️⃣ Process only successful payments
    if str(data.status).lower() != "successful":
        return {"status": "ignored_not_successful"}

    # 3️⃣ Idempotency check (prevent duplicate processing)
    already_processed = (
        db.query(Ticket)
        .filter(Ticket.tx_ref.startswith(data.tx_ref))
        .first()
    )
    if already_processed:
        return {"status": "already_processed"}

    tickets_created = []

    # 4️⃣ Get attendees list from meta
    attendees = data.meta.attendees if data.meta and data.meta.attendees else []

    # If frontend did not send attendees → assume single ticket
    if not attendees:
        class FallbackAttendee:
            full_name = data.customer.name
            gender = "N/A"
            department = "N/A"
            level = "N/A"
            price = Decimal(data.amount)

        attendees = [FallbackAttendee()]

    total_amount = Decimal(data.amount)
    split_price = total_amount / len(attendees)

    # 5️⃣ Create tickets
    for attendee in attendees:
        ticket_id = generate_ticket_id()
        qr_data = encrypt_qr_payload(ticket_id)

        # 🔥 Stored tx_ref = original + ticketId
        stored_tx_ref = f"{data.tx_ref}-{ticket_id}"

        price = Decimal(attendee.price) if attendee.price else split_price

        ticket = create_ticket(
            db,
            {
                "id": ticket_id,
                "tx_ref": stored_tx_ref,
                "full_name": attendee.full_name,
                "email": data.customer.email,
                "phone": data.customer.phone_number or "",
                "department": attendee.department,
                "level": attendee.level,
                "gender": attendee.gender,
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

    # 6️⃣ Commit once after all tickets
    db.commit()

    return {
        "status": "success",
        "tickets_created": len(tickets_created),
        "tickets": tickets_created,
    }
