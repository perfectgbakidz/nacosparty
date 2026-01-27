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
    db: Session = Depends(get_db)
):
    # 🔐 Verify signature (DO NOT throw)
    signature = request.headers.get("verif-hash")
    if signature != FLW_SECRET_HASH:
        return {"status": "ignored"}  # Always 200

    data = payload.data

    if data.status != "successful":
        return {"status": "ignored"}

    # 🔁 Idempotency (VERY IMPORTANT)
    if get_ticket_by_tx_ref(db, data.tx_ref):
        return {"status": "already_processed"}

    ticket_id = generate_ticket_id()

    ticket = create_ticket(
        db,
        {
            "id": ticket_id,
            "tx_ref": data.tx_ref,
            "full_name": data.customer.name,
            "email": data.customer.email,
            "phone": data.customer.phone_number or "N/A",
            "department": "NACOS",
            "level": "N/A",
            "gender": "N/A",
            "price": data.amount,
            "currency": data.currency,
            "payment_status": "paid",
        }
    )

    qr_data = encrypt_qr_payload(ticket.id)

    return {
        "status": "success",
        "ticketId": ticket.id,
        "qrData": qr_data
    }
