from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from decimal import Decimal


class TicketResponse(BaseModel):
    id: str
    full_name: str = Field(..., alias="fullName")
    email: EmailStr
    phone: str
    department: str
    level: str
    gender: str
    price: Decimal
    currency: str
    payment_status: str = Field(..., alias="paymentStatus")
    purchase_date: datetime = Field(..., alias="purchaseDate")
    is_checked_in: bool = Field(..., alias="checkedIn")
    qr_data: str = Field(..., alias="qrData")

    class Config:
        from_attributes = True
        populate_by_name = True


class TicketAvailabilityRequest(BaseModel):
    email: EmailStr
    phone: str


class TicketAvailabilityResponse(BaseModel):
    available: bool
    reason: str | None = None
