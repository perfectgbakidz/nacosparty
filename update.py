import requests
from sqlalchemy.orm import Session
from database.session import SessionLocal
from models.ticket import Ticket

FLW_SECRET_KEY = "import requests
from sqlalchemy.orm import Session
from database.session import SessionLocal
from models.ticket import Ticket

FLW_SECRET_KEY = "FLWSECK-xxxxxxxxxxxx"

headers = {
    "Authorization": f"Bearer {FLW_SECRET_KEY}",
    "Content-Type": "application/json",
}

url = "https://api.flutterwave.com/v3/transactions"

db: Session = SessionLocal()

response = requests.get(url, headers=headers)
data = response.json()

for tx in data.get("data", []):
    if tx["status"] != "successful":
        continue

    tx_ref = tx["tx_ref"]

    # check if already saved
    exists = db.query(Ticket).filter(Ticket.tx_ref == tx_ref).first()
    if exists:
        continue

    ticket = Ticket(
        tx_ref=tx_ref,
        amount=tx["amount"],
        currency=tx["currency"],
        email=tx["customer"]["email"],
        status="paid",
    )
    db.add(ticket)

db.commit()
db.close()

print("✅ Transactions synced successfully")
"

headers = {
    "Authorization": f"Bearer {FLW_SECRET_KEY}",
    "Content-Type": "application/json",
}

url = "https://api.flutterwave.com/v3/transactions"

db: Session = SessionLocal()

response = requests.get(url, headers=headers)
data = response.json()

for tx in data.get("data", []):
    if tx["status"] != "successful":
        continue

    tx_ref = tx["tx_ref"]

    # check if already saved
    exists = db.query(Ticket).filter(Ticket.tx_ref == tx_ref).first()
    if exists:
        continue

    ticket = Ticket(
        tx_ref=tx_ref,
        amount=tx["amount"],
        currency=tx["currency"],
        email=tx["customer"]["email"],
        status="paid",
    )
    db.add(ticket)

db.commit()
db.close()

print("✅ Transactions synced successfully")
