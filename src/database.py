import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
<<<<<<< HEAD
from sqlalchemy.pool import StaticPool
=======


>>>>>>> c5fd1cb4d527d08897f7869b3b5b436390e09411

load_dotenv()

database_url = os.getenv("DATABASE_URL", "sqlite:///:memory:")

# Use StaticPool for SQLite in-memory so all threads/sessions share the same tables
if "sqlite" in database_url:
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()