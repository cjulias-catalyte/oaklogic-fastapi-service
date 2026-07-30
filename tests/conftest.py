import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from src.database import Base, SessionLocal, engine, get_db
from src.main import app


@pytest.fixture(autouse=True)
def setup_postgres_db():
    # 1. Ensure tables exist first
    Base.metadata.create_all(bind=engine)

    # 2. Wipe data for a clean slate
    db = SessionLocal()
    try:
        db.execute(
            text("TRUNCATE TABLE product, category RESTART IDENTITY CASCADE;")
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

    yield

    # 3. Clean up after test finishes
    db = SessionLocal()
    try:
        db.execute(
            text("TRUNCATE TABLE product, category RESTART IDENTITY CASCADE;")
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


@pytest.fixture
def client():
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()