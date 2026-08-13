"""Database engine, session management, and declarative Base."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from .config import settings


connect_args = {}

# Aiven MySQL requires SSL.
ssl_ca = os.getenv("MYSQL_SSL_CA")

if ssl_ca:
    connect_args["ssl"] = {
        "ca": ssl_ca,
    }


engine = create_engine(
    settings.resolved_database_url,
    pool_pre_ping=True,
    pool_recycle=280,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

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
