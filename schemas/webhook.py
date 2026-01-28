from pydantic import BaseModel, EmailStr
from typing import List, Optional
from decimal import Decimal


class FlutterwaveCustomer(BaseModel):
    name: strfrom pydantic import BaseModel, EmailStr
from typing import List, Optional, Any
from decimal import Decimal


class FlutterwaveCustomer(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None


class AttendeeMeta(BaseModel):
    full_name: str
    gender: Optional[str] = "N/A"         # default if missing
    department: Optional[str] = "NACOS"   # default if missing
    level: Optional[str] = "N/A"          # default if missing
    price: Optional[Decimal] = None        # per-ticket price from frontend


class FlutterwaveMeta(BaseModel):
    attendees: Optional[List[AttendeeMeta]] = []  # default empty list


class FlutterwaveData(BaseModel):
    id: Any  # allow int or str
    tx_ref: str
    amount: Any  # allow str or number
    currency: str
    status: str
    customer: FlutterwaveCustomer
    meta: Optional[FlutterwaveMeta] = None


class FlutterwaveWebhookPayload(BaseModel):
    event: str
    data: FlutterwaveData

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
