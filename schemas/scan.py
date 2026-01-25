from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    qr_data: str = Field(..., alias="qrData")

    class Config:
        populate_by_name = True


class ScanResponse(BaseModel):
    ticket_id: str = Field(..., alias="ticketId")
    full_name: str = Field(..., alias="fullName")
    checked_in: bool = Field(..., alias="checkedIn")
    message: str

    class Config:
        populate_by_name = True
