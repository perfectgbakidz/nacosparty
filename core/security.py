import bcrypt
from datetime import datetime, timedelta
import jwt
from core.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

# =========================
# Password Hashing
# =========================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


# =========================
# JWT
# =========================
def create_access_token() -> str:
    payload = {
        "sub": "super_admin",
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
