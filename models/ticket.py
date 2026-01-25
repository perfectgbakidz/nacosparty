from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Numeric,
    UniqueConstraint
)
from sqlalchemy.sql import func
from database.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, index=True)

    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False, index=True)

    department = Column(String, nullable=False)
    level = Column(String, nullable=False)
    gender = Column(String, nullable=False)

    price = Column(Numeric(10, 2), nullable=False)

    purchase_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    is_checked_in = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("email", name="uq_ticket_email"),
        UniqueConstraint("phone", name="uq_ticket_phone"),
    )
