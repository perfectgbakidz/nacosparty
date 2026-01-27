from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Numeric,
    Index
)
from sqlalchemy.sql import func
from database.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    # Public ticket ID (used in QR)
    id = Column(String, primary_key=True, index=True)

    # Flutterwave
    tx_ref = Column(String, nullable=False, unique=True, index=True)
    payment_status = Column(String, nullable=False)
    currency = Column(String, nullable=False)

    # Customer
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True, index=True)

    # Event info
    department = Column(String, nullable=False)
    level = Column(String, nullable=False)
    gender = Column(String, nullable=False)

    # Payment
    price = Column(Numeric(10, 2), nullable=False)

    # Metadata
    purchase_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    is_checked_in = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_ticket_email_phone", "email", "phone"),
    )
