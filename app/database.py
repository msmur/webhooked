import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the database URL from the environment
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

engine = create_engine(DB_CONNECTION_STRING, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
