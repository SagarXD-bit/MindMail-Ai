"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

import sys
import os

# Ensure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base, get_db
from app.models import User, Email, AIClassification
from app.main import app
from app.seed_data import get_demo_emails


@pytest.fixture(scope="function")
def db_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    db = TestingSessionLocal()

    # Create a default user
    user = User(name="Test User", email="test@test.com")
    db.add(user)
    db.commit()
    db.refresh(user)

    yield db
    db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a FastAPI TestClient with the test database."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seeded_db(db_session):
    """Seed the test database with demo emails."""
    user = db_session.query(User).first()
    demo_data = get_demo_emails()
    for i, item in enumerate(demo_data):
        email = Email(
            user_id=user.id,
            message_id=f"test-demo-{i}",
            sender_email=item["sender_email"],
            sender_name=item.get("sender_name"),
            recipient_email="test@test.com",
            subject=item["subject"],
            body_text=item["body_text"],
            preview=item["body_text"][:200],
            received_at=item["received_at"],
            status="unread",
            is_demo=True,
        )
        db_session.add(email)
        db_session.flush()
        cls = AIClassification(
            email_id=email.id,
            category=item["category"],
            urgency=item["urgency"],
            confidence=item["confidence"],
            explanation=item["explanation"],
            needs_response=item.get("needs_response", False),
            suggested_followup=item.get("suggested_followup", False),
        )
        db_session.add(cls)
    db_session.commit()
    return db_session
