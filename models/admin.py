from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from database.base import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(String, primary_key=True, index=True)
    password_hash = Column(String, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
