# schemas/ticket.py

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


# -----------------------------
# Request Schemas (ADMIN / INTERNAL)
# -----------------------------
class TicketAttendeeCreate(BaseModel):
    full_name: str
    gender: Optional[str] = "N/A"
    department: Optional[str] = "NACOS"
    level: Optional[str] = "N/A"
    price: Optional[Decimal] = None


class AdminTicketCreateRequest(BaseModel):
    tx_ref: str
    email: EmailStr
    phone: str
    attendees: List[TicketAttendeeCreate]


class TicketAvailabilityRequest(BaseModel):
    email: EmailStr
    phone: str


# -----------------------------
# Response Schemas
# -----------------------------
class TicketResponse(BaseModel):
    id: str
    tx_ref: str
    full_name: str
    email: EmailStr
    phone: str
    department: str
    level: str
    gender: str
    price: Decimal
    currency: str
    payment_status: str
    qr_data: str
    purchase_date: datetime

    class Config:
        orm_mode = True


class TicketAvailabilityResponse(BaseModel):
    available: bool
    reason: Optional[str] = None
