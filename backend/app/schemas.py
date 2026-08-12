"""Pydantic v2 request/response schemas for MailMind AI."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---- Health ----
class HealthResponse(BaseModel):
    status: str
    database: str


# ---- Accounts ----
class EmailAccountCreate(BaseModel):
    email_address: EmailStr
    imap_server: str
    imap_port: int = 993
    imap_ssl: bool = True
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = 587
    smtp_ssl: bool = True
    password: str = Field(..., min_length=1, description="Email account password (encrypted before storage)")


class EmailAccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email_address: str
    imap_server: str
    imap_port: int
    imap_ssl: bool
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_ssl: bool = True
    status: str
    last_sync_at: Optional[datetime] = None
    created_at: datetime


# ---- Emails ----
class AIClassificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    category: str
    urgency: str
    confidence: float
    explanation: Optional[str] = None
    needs_response: bool = False
    suggested_followup: bool = False
    is_manual_override: bool = False


class ReplySuggestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tone: str
    content: str
    status: str
    created_at: datetime


class FollowUpBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    reminder_at: datetime


class EmailBrief(BaseModel):
    """Lightweight email representation for lists."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    sender_email: str
    sender_name: Optional[str] = None
    subject: str
    preview: Optional[str] = None
    received_at: datetime
    status: str
    is_demo: bool
    classification: Optional[AIClassificationOut] = None
    has_replies: bool = False
    has_followup: bool = False


class EmailDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sender_email: str
    sender_name: Optional[str] = None
    recipient_email: str
    subject: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    preview: Optional[str] = None
    received_at: datetime
    status: str
    is_demo: bool
    responded_at: Optional[datetime] = None
    classification: Optional[AIClassificationOut] = None
    replies: List[ReplySuggestionOut] = []
    follow_ups: List[FollowUpBrief] = []
    thread: List["EmailBrief"] = []


class EmailListResponse(BaseModel):
    emails: List[EmailBrief]
    total: int
    page: int
    page_size: int


class ClassificationUpdate(BaseModel):
    category: Optional[str] = None
    urgency: Optional[str] = None


class EmailStatusUpdate(BaseModel):
    status: str  # unread / read / responded / archived


# ---- Replies ----
class ReplyGenerate(BaseModel):
    tone: str = "professional"  # professional / friendly / concise


class ReplyUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None  # draft / used / discarded


class SendReplyRequest(BaseModel):
    reply_id: int
    confirm: bool = Field(..., description="Must be true to send")


# ---- Follow-ups ----
class FollowUpCreate(BaseModel):
    email_id: int
    reminder_at: datetime
    note: Optional[str] = None


class FollowUpUpdate(BaseModel):
    reminder_at: Optional[datetime] = None
    note: Optional[str] = None
    status: Optional[str] = None  # pending / completed / snoozed


class FollowUpOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email_id: int
    reminder_at: datetime
    note: Optional[str] = None
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    email: Optional[EmailBrief] = None


# ---- Analytics ----
class AnalyticsResponse(BaseModel):
    total_emails: int
    emails_by_category: dict
    emails_by_urgency: dict
    emails_requiring_response: int
    emails_responded_to: int
    pending_responses: int
    avg_response_time_hours: Optional[float] = None
    follow_ups_completed: int
    follow_ups_overdue: int
    follow_ups_upcoming: int
    ai_accuracy: float
    reply_suggestions_generated: int
    reply_suggestions_used: int
    response_rate: float
    recent_trend: List[dict]


# ---- Settings ----
class SettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    default_reply_tone: str
    auto_categorize: bool
    categorization_aggressiveness: str
    notifications_enabled: bool
    email_notifications: bool
    store_email_bodies: bool


class SettingsUpdate(BaseModel):
    default_reply_tone: Optional[str] = None
    auto_categorize: Optional[bool] = None
    categorization_aggressiveness: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None
    store_email_bodies: Optional[bool] = None


# ---- Sync ----
class SyncResponse(BaseModel):
    status: str
    new_emails: int
    total_emails: int
    message: str
    mode: str  # "imap" / "demo"


# ---- Generic ----
class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
