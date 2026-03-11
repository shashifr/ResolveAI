from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# SQLite database file path
DATABASE_URL = "sqlite:///sentinel.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # Required for SQLite with multi-threading
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models import Base
    Base.metadata.create_all(bind=engine)
