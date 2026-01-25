from sqlalchemy.orm import Session
from models.admin import Admin


# =========================
# Read
# =========================
def get_admin(db: Session) -> Admin | None:
    """
    Returns the single super admin.
    Assumes only one admin row exists.
    """
    return db.query(Admin).filter(Admin.is_active == True).first()


# =========================
# Create (one-time use)
# =========================
def create_admin(db: Session, admin_id: str, password_hash: str) -> Admin:
    admin = Admin(
        id=admin_id,
        Dansugar2026=password_hash
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin
