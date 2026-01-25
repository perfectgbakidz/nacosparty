from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from schemas.webhook import FlutterwaveWebhookPayload
from crud.ticket import create_ticket, get_ticket_by_email, get_ticket_by_phone
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
    signature = request.headers.get("verif-hash")
    if signature != FLW_SECRET_HASH:
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = payload.data

    if data.status != "successful":
        return {"message": "Payment not successful"}

    # Enforce 1 ticket per person
    if get_ticket_by_email(db, data.customer.email):
        return {"message": "Duplicate ticket ignored"}

    if data.customer.phone_number and get_ticket_by_phone(db, data.customer.phone_number):
        return {"message": "Duplicate ticket ignored"}

    ticket_id = generate_ticket_id()

    ticket = create_ticket(
        db,
        {
            "id": ticket_id,
            "full_name": data.customer.name,
            "email": data.customer.email,
            "phone": data.customer.phone_number or "N/A",
            "department": "NACOS",
            "level": "N/A",
            "gender": "N/A",
            "price": data.amount,
        }
    )

    encrypted_qr = encrypt_qr_payload(ticket.id)

    return {
        "message": "Ticket created",
        "ticketId": ticket.id,
        "qrData": encrypted_qr
    }
