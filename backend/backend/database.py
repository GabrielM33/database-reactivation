import logging
import os
import re
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logger = logging.getLogger(__name__)

# Get database URL from environment variable or use SQLite default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# Handle special case for Neon PostgreSQL URLs
if DATABASE_URL.startswith("postgres://"):
    # Convert postgres:// to postgresql:// for SQLAlchemy
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Log which database system is being used
if DATABASE_URL.startswith("sqlite"):
    logger.info("Using SQLite database")
elif DATABASE_URL.startswith("postgresql"):
    logger.info("Using PostgreSQL database")
    # Parse the URL to get the hostname
    parsed_url = urlparse(DATABASE_URL)
    logger.info(f"Database host: {parsed_url.hostname}")
else:
    logger.info(f"Using database with URL: {DATABASE_URL[:20]}...")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import models to ensure they're registered with the Base
from backend.models import Base, Conversation, Lead, Message


# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Function to initialize the database
def init_db(force_create_tables=False):
    """Initialize the database and create tables if they don't exist.

    Args:
        force_create_tables: If True, will drop all tables before creating them.
    """
    if force_create_tables and not DATABASE_URL.startswith("sqlite"):
        # This will drop all tables - be careful!
        logger.warning("Dropping all tables due to force_create_tables=True")
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")
