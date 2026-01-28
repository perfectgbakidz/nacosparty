from sqlalchemy.orm import Session
from models.ticket import Ticket

# =========================
# Create
# =========================
def create_ticket(db: Session, ticket_data: dict) -> Ticket:
    ticket = Ticket(**ticket_data)
    db.add(ticket)
    db.refresh(ticket) # Refresh to get updated fields (like purchase_date)
    return ticket

# =========================
# Read
# =========================
def get_ticket_by_id(db: Session, ticket_id: str) -> Ticket | None:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()

def get_ticket_by_email(db: Session, email: str) -> Ticket | None:
    return db.query(Ticket).filter(Ticket.email == email).first()

def get_ticket_by_phone(db: Session, phone: str) -> Ticket | None:
    return db.query(Ticket).filter(Ticket.phone == phone).first()

def get_ticket_by_tx_ref(db: Session, tx_ref: str) -> Ticket | None:
    return db.query(Ticket).filter(Ticket.tx_ref == tx_ref).first()

def get_all_tickets(db: Session):
    return (
        db.query(Ticket)
        .order_by(Ticket.purchase_date.desc())
        .all()
    )

# =========================
# Update
# =========================
def mark_ticket_checked_in(db: Session, ticket: Ticket) -> Ticket:
    ticket.is_checked_in = True
    db.commit()
    db.refresh(ticket)
    return ticket

# =========================
# Delete
# =========================
def delete_ticket(db: Session, ticket: Ticket):
    db.delete(ticket)
    db.commit()
