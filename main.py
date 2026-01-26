from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import auth, tickets, scan, webhook
from database.session import engine
from database.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NACOS MAPOLY Ticketing API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nacosfresherspartyticket.vercel.app/"],
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

# Routers
app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(scan.router)
app.include_router(webhook.router)

# Health / Ping endpoint
@app.get("/ping")
async def ping():
    """
    Endpoint your bot can ping every 2 min to keep server alive.
    Returns a simple status message.
    """
    return {"status": "ok", "message": "Server is alive"}
