from sqlalchemy import Column, String, Boolean, DateTime, Numeric
from sqlalchemy.sql import func
from database.base import Base
import uuid


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Shared contact info (same for all tickets in an order)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    # Attendee-specific info
    full_name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    level = Column(String, nullable=False)

    # Payment linkage
    tx_ref = Column(String, index=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, nullable=False)
    payment_status = Column(String, nullable=False)

    # QR & check-in
    qr_data = Column(String, unique=True, nullable=True)  # ← MUST be nullable
    is_checked_in = Column(Boolean, default=False)

    purchase_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
