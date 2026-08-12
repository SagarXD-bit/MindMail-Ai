"""SQLAlchemy ORM models for MailMind AI."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    accounts = relationship("EmailAccount", back_populates="user", cascade="all, delete-orphan")
    emails = relationship("Email", back_populates="user", cascade="all, delete-orphan")
    follow_ups = relationship("FollowUp", back_populates="user", cascade="all, delete-orphan")


class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email_address = Column(String(255), nullable=False)
    imap_server = Column(String(255), nullable=False)
    imap_port = Column(Integer, default=993)
    imap_ssl = Column(Boolean, default=True)
    smtp_server = Column(String(255), nullable=True)
    smtp_port = Column(Integer, nullable=True)
    smtp_ssl = Column(Boolean, default=True)
    encrypted_password = Column(Text, nullable=False)
    status = Column(String(20), default="disconnected")  # connected / error / demo / disconnected
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="accounts")
    emails = relationship("Email", back_populates="account")


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(Integer, ForeignKey("email_accounts.id", ondelete="SET NULL"), nullable=True)
    message_id = Column(String(500), nullable=True, index=True)
    thread_id = Column(String(500), nullable=True, index=True)
    sender_email = Column(String(255), nullable=False)
    sender_name = Column(String(255), nullable=True)
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False, default="(No Subject)")
    body_text = Column("body_text", Text(length=16777215), nullable=True)
    body_html = Column("body_html", Text(length=16777215), nullable=True)
    preview = Column(String(300), nullable=True)
    received_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(20), default="unread")  # unread / read / responded / archived
    is_demo = Column(Boolean, default=False)
    responded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="emails")
    account = relationship("EmailAccount", back_populates="emails")
    classification = relationship("AIClassification", back_populates="email", uselist=False, cascade="all, delete-orphan")
    replies = relationship("ReplySuggestion", back_populates="email", cascade="all, delete-orphan")
    follow_ups = relationship("FollowUp", back_populates="email", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="email", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_emails_user_status", "user_id", "status"),
        Index("ix_emails_user_received", "user_id", "received_at"),
    )


class AIClassification(Base):
    __tablename__ = "ai_classifications"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, unique=True)
    category = Column(String(40), nullable=False)
    urgency = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    explanation = Column(Text, nullable=True)
    needs_response = Column(Boolean, default=False)
    suggested_followup = Column(Boolean, default=False)
    is_manual_override = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    email = relationship("Email", back_populates="classification")


class ReplySuggestion(Base):
    __tablename__ = "reply_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False)
    tone = Column(String(20), nullable=False)  # professional / friendly / concise
    content = Column("content", Text(length=16777215), nullable=False)
    status = Column(String(20), default="draft")  # draft / used / discarded
    created_at = Column(DateTime, default=datetime.utcnow)

    email = relationship("Email", back_populates="replies")


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False)
    reminder_at = Column(DateTime, nullable=False)
    note = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending / completed / snoozed
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="follow_ups")
    email = relationship("Email", back_populates="follow_ups")


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False)
    original_category = Column(String(40), nullable=False)
    corrected_category = Column(String(40), nullable=False)
    original_urgency = Column(String(20), nullable=False)
    corrected_urgency = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    email = relationship("Email", back_populates="feedback")


class UserSettings(Base):
    """Key-value store for user preferences."""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    default_reply_tone = Column(String(20), default="professional")
    auto_categorize = Column(Boolean, default=True)
    categorization_aggressiveness = Column(String(20), default="balanced")  # conservative / balanced / aggressive
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    store_email_bodies = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
