import uuid

def generate_ticket_id() -> str:
    """
    Generates a unique ticket ID like:
    NACOS-8F3A2C9D
    """
    short_id = uuid.uuid4().hex[:8].upper()
    return f"NACOS-{short_id}"
