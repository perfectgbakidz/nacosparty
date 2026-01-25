from fastapi import Header, HTTPException, status
from core.security import decode_access_token


def super_admin_required(authorization: str = Header(...)):
    """
    Dependency to protect admin-only routes
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    token = authorization.split(" ")[1]

    try:
        payload = decode_access_token(token)
        if payload.get("sub") != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
