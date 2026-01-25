from database.session import engine
from database.base import Base
from models.ticket import Ticket
from models.admin import Admin

Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully")
