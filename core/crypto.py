import json
from cryptography.fernet import Fernet, InvalidToken
from core.config import QR_SECRET


# Ensure key is bytes
fernet = Fernet(QR_SECRET.encode())


def encrypt_qr_payload(ticket_id: str) -> str:
    """
    Encrypts ticket payload for QR code
    """
    payload = {"ticket_id": ticket_id}
    json_payload = json.dumps(payload).encode()
    encrypted = fernet.encrypt(json_payload)
    return encrypted.decode()


def decrypt_qr_payload(encrypted_data: str) -> str:
    """
    Decrypts QR payload and returns ticket_id
    """
    try:
        decrypted = fernet.decrypt(encrypted_data.encode())
        payload = json.loads(decrypted.decode())
        return payload["ticket_id"]
    except (InvalidToken, KeyError, json.JSONDecodeError):
        raise ValueError("Invalid or tampered QR code")
