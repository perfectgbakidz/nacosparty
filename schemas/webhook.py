from pydantic import BaseModel, EmailStr
from typing import List, Optional
from decimal import Decimal


class FlutterwaveCustomer(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None


class AttendeeMeta(BaseModel):
    full_name: str
    gender: str
    department: str
    level: str
    price: Decimal  # per-ticket price from frontend


class FlutterwaveMeta(BaseModel):
    attendees: List[AttendeeMeta]


class FlutterwaveData(BaseModel):
    id: int
    tx_ref: str
    amount: Decimal
    currency: str
    status: str
    customer: FlutterwaveCustomer
    meta: Optional[FlutterwaveMeta] = None


class FlutterwaveWebhookPayload(BaseModel):
    event: str
    data: FlutterwaveData
