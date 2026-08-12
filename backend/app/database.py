"""Database engine, session management, and declarative Base."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from .config import settings

engine = create_engine(
    settings.resolved_database_url,
    pool_pre_ping=True,
    pool_recycle=280,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables (used as fallback / for first run)."""
    Base.metadata.create_all(bind=engine)
