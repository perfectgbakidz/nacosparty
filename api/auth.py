from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.auth import AdminLoginRequest, AdminLoginResponse
from crud.admin import get_admin
from core.security import verify_password, create_access_token
from database.session import SessionLocal

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=AdminLoginResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = get_admin(db)

    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token()
    return {
        "token": token,
        "session_expiry": "2 hours"
    }
