from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from decimal import Decimal


class TicketBase(BaseModel):
    full_name: str = Field(..., alias="fullName")
    email: EmailStr
    phone: str
    department: str
    level: str
    gender: str
    price: Decimal
    purchase_date: datetime = Field(..., alias="purchaseDate")
    is_checked_in: bool = Field(False, alias="checkedIn")

    class Config:
        populate_by_name = True


class TicketResponse(TicketBase):
    id: str

    class Config:
        populate_by_name = True
        from_attributes = True


class TicketAvailabilityRequest(BaseModel):
    email: EmailStr
    phone: str


class TicketAvailabilityResponse(BaseModel):
    available: bool
    reason: str | None = None
