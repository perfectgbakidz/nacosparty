from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import auth, tickets, scan, webhook
from database.session import engine
from database.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NACOS MAPOLY Ticketing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(scan.router)
app.include_router(webhook.router)
