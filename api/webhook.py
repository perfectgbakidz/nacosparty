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
    # -----------------------------
    # 1. Verify Flutterwave webhook
    # -----------------------------
    signature = request.headers.get("verif-hash")
    if signature != FLW_SECRET_HASH:
        return {"status": "ignored"}

    data = payload.data

    # -----------------------------
    # 2. Only process successful payments
    # -----------------------------
    if str(data.status).lower() != "successful":
        return {"status": "ignored"}

    # -----------------------------
    # 3. Prevent duplicate processing
    # -----------------------------
    if get_ticket_by_tx_ref(db, str(data.tx_ref)):
        return {"status": "already_processed"}

    tickets_created = []

    # -----------------------------
    # 4. Extract attendees safely
    # -----------------------------
    attendees = []
    if data.meta and data.meta.attendees:
        attendees = data.meta.attendees

    # Fallback: create one ticket if no attendees sent
    if not attendees:
        attendees = [
            {
                "full_name": data.customer.name,
                "gender": "N/A",
                "department": "NACOS",
                "level": "N/A",
                "price": Decimal(data.amount),
            }
        ]

    # -----------------------------
    # 5. Create tickets
    # -----------------------------
    for attendee in attendees:
        # attendee IS A DICT — NOT an object
        ticket_id = generate_ticket_id()
        qr_data = encrypt_qr_payload(ticket_id)

        price = (
            Decimal(attendee.get("price"))
            if attendee.get("price") is not None
            else Decimal(data.amount)
        )

        ticket = create_ticket(
            db,
            {
                "id": ticket_id,
                "tx_ref": str(data.tx_ref),
                "full_name": attendee.get("full_name"),
                "email": data.customer.email,
                "phone": data.customer.phone_number or "",
                "department": attendee.get("department", "N/A"),
                "level": attendee.get("level", "N/A"),
                "gender": attendee.get("gender", "N/A"),
                "price": price,
                "currency": data.currency,
                "payment_status": data.status,
                "qr_data": qr_data,
            },
        )

        tickets_created.append(
            {
                "ticketId": ticket.id,
                "qrData": qr_data,
                "full_name": ticket.full_name,
            }
        )

    # -----------------------------
    # 6. Commit ONCE
    # -----------------------------
    db.commit()

    return {
        "status": "success",
        "tickets": tickets_created,
    }
