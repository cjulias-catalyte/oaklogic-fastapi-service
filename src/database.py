import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

load_dotenv()

# Defaults to an in-memory SQLite database if DATABASE_URL is not set in your .env file
database_url = os.getenv("DATABASE_URL", "sqlite:///:memory:")

# Use StaticPool and disable same-thread checks only when using SQLite
if "sqlite" in database_url:
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # Standard connection pooling for PostgreSQL (psycopg2)
    engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request
    and ensures it closes automatically when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()