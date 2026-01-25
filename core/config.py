import os

# =========================
# Database
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# =========================
# JWT
# =========================
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not set")

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 120

# =========================
# Flutterwave
# =========================
FLW_SECRET_HASH = os.getenv("FLW_SECRET_HASH")
if not FLW_SECRET_HASH:
    raise RuntimeError("FLW_SECRET_HASH is not set")

# =========================
# QR Encryption
# =========================
QR_SECRET = os.getenv("QR_SECRET")
if not QR_SECRET:
    raise RuntimeError("QR_SECRET_KEY is not set")
