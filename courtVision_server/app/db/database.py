import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings  # Import settings from config.py

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# 🔹 MongoDB Configuration (Real-time Stats)
mongo_client = AsyncIOMotorClient(settings.mongo_database_url)
mongo_db = mongo_client[settings.MONGO_DB]  # Use the MONGO_DB setting

# 🔹 PostgreSQL Configuration (Historical Data)
engine = create_engine(settings.postgres_database_url, echo=True)  # Use the postgres_database_url property from Settings
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

# Dependency for getting the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create tables
def create_db():
    Base.metadata.create_all(bind=engine)

# Run the function to create tables (only if needed, ensure this doesn't run on every startup)
#create_db()

