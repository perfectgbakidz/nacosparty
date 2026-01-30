from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from decimal import Decimal
import json  # Needed to parse stringified JSON

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

    tickets_created = []

    # 3️⃣ Parse meta.attendees (stringified JSON) into list
    attendees = []
    if data.meta and data.meta.attendees:
        try:
            attendees = json.loads(data.meta.attendees)  # <-- parse string to list
        except Exception:
            # fallback: single attendee if parsing fails
            attendees = [{
                "full_name": data.customer.name,
                "gender": "N/A",
                "department": "NACOS",
                "level": "N/A",
                "price": Decimal(data.amount),
                "email": data.customer.email,
                "phone": data.customer.phone_number or ""
            }]
    else:
        # fallback: single attendee if meta missing
        attendees = [{
            "full_name": data.customer.name,
            "gender": "N/A",
            "department": "NACOS",
            "level": "N/A",
            "price": Decimal(data.amount),
            "email": data.customer.email,
            "phone": data.customer.phone_number or ""
        }]

    # 4️⃣ Calculate price per attendee if missing
    total_amount = Decimal(data.amount)
    num_attendees = len(attendees)
    if num_attendees == 0:
        num_attendees = 1  # avoid division by zero
    split_price = total_amount / num_attendees

    # 5️⃣ Create tickets
    for attendee in attendees:
        ticket_id = generate_ticket_id()
        qr_data = encrypt_qr_payload(ticket_id)

        price = Decimal(attendee.get("price")) if attendee.get("price") else split_price

        # Make tx_ref unique per ticket
        stored_tx_ref = f"{data.tx_ref}-{ticket_id}"

        ticket = create_ticket(
            db,
            {
                "id": ticket_id,
                "tx_ref": stored_tx_ref,
                "full_name": attendee.get("full_name") or data.customer.name,
                "email": attendee.get("email") or data.customer.email,
                "phone": attendee.get("phone") or data.customer.phone_number or "",
                "department": attendee.get("department") or "NACOS",
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
            "qrData": qr_data
        })

    # 6️⃣ Commit all tickets at once
    db.commit()

    return {
        "status": "success",
        "tickets_created": len(tickets_created),
        "tickets": tickets_created,
    }
