from pydantic import BaseModel, EmailStr
from typing import Optional


class FlutterwaveCustomer(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None


class FlutterwaveData(BaseModel):
    id: int
    tx_ref: str
    amount: float
    currency: str
    status: str
    customer: FlutterwaveCustomer


class FlutterwaveWebhookPayload(BaseModel):
    event: str
    data: FlutterwaveData
