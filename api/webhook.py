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

    # 2️⃣ Only process successful payments
    if str(data.status).lower() != "successful":
        return {"status": "ignored_not_successful"}

    # 3️⃣ Parse attendees safely
    attendees = []
    if data.meta and data.meta.attendees:
        try:
            attendees = json.loads(data.meta.attendees)
        except Exception:
            attendees = []

    # Fallback: single attendee if meta missing
    if not attendees:
        attendees = [{
            "full_name": data.customer.name,
            "email": data.customer.email,
            "phone": data.customer.phone_number or "",
            "gender": "N/A",
            "department": "N/A",
            "level": "N/A",
            "price": Decimal(data.amount)
        }]

    tickets_created = []

    # 4️⃣ Loop through each attendee
    for attendee in attendees:
        # Map frontend keys just in case
        fname = attendee.get("full_name") or attendee.get("fullName")
        email = attendee.get("email") or data.customer.email
        phone = attendee.get("phone") or data.customer.phone_number or ""
        gender = attendee.get("gender") or "N/A"
        department = attendee.get("department") or "N/A"
        level = attendee.get("level") or "N/A"
        price = Decimal(attendee.get("price", 0)) or (Decimal(data.amount) / len(attendees))

        # 5️⃣ Idempotency check per attendee
        ticket_exists = db.query(Ticket).filter(
            Ticket.full_name == fname,
            Ticket.tx_ref.contains(data.tx_ref)
        ).first()
        if ticket_exists:
            continue  # Skip this attendee if already exists

        # 6️⃣ Generate ticket
        ticket_id = generate_ticket_id()
        qr_data = encrypt_qr_payload(ticket_id)
        unique_tx_ref = f"{data.tx_ref}-{ticket_id}"

        ticket = create_ticket(
            db,
            {
                "id": ticket_id,
                "tx_ref": unique_tx_ref,
                "full_name": fname,
                "email": email,
                "phone": phone,
                "department": department,
                "level": level,
                "gender": gender,
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

    # 7️⃣ Commit all new tickets at once
    if tickets_created:
        db.commit()
        return {"status": "success", "tickets_created": len(tickets_created), "tickets": tickets_created}

    return {"status": "already_processed"}
