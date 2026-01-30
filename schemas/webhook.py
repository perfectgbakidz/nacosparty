from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any
from decimal import Decimal


class FlutterwaveCustomer(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None


class AttendeeMeta(BaseModel):
    full_name: str
    gender: Optional[str] = "N/A"
    department: Optional[str] = "NACOS"
    level: Optional[str] = "N/A"
    price: Optional[Decimal] = None

class FlutterwaveMeta(BaseModel):
    attendees: str = ""  # stringified JSON from frontend


class FlutterwaveData(BaseModel):
    id: Any
    tx_ref: str
    amount: Any
    currency: str
    status: str
    customer: FlutterwaveCustomer
    meta: Optional[FlutterwaveMeta] = None


class FlutterwaveWebhookPayload(BaseModel):
    event: str
    data: FlutterwaveData
