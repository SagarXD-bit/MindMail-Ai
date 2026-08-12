"""FastAPI application entrypoint for MailMind AI."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .config import settings
from .database import init_db, get_db
from .routers import health, settings as settings_router, accounts, emails, replies, follow_ups, analytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    logger.info("MailMind AI backend starting up...")
    init_db()
    logger.info("Database initialized.")
    yield
    logger.info("MailMind AI backend shutting down.")


app = FastAPI(
    title="MailMind AI",
    description="AI Email Automation Tool — categorize, reply, follow up, analyze.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
origins = [o.strip() for o in settings.cors_origins.split(",")] if settings.cors_origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(emails.router, prefix="/api")
app.include_router(replies.router, prefix="/api")
app.include_router(follow_ups.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

# Also add sync endpoint at /api/sync (alias for /api/accounts/sync)
@app.post("/api/sync")
def sync_alias(force_demo: bool = False, db: Session = Depends(get_db)):
    """Top-level sync endpoint — delegates to the accounts sync logic."""
    return accounts.sync_emails(force_demo=force_demo, db=db)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and return a clean JSON error."""
    # HTTPException subclasses have already been handled by FastAPI
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


@app.get("/")
def root():
    return {"app": "MailMind AI", "version": "1.0.0", "docs": "/docs"}
