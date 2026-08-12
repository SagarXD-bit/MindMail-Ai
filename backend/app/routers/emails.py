"""Emails router — list (search/filter/sort/paginate), detail, status, classification override."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, case
from typing import Optional
from ..database import get_db
from ..models import Email, AIClassification, User, UserFeedback, FollowUp, ReplySuggestion
from ..schemas import (
    EmailListResponse, EmailBrief, EmailDetail, EmailStatusUpdate,
    ClassificationUpdate, AIClassificationOut, ReplySuggestionOut, FollowUpBrief
)
from .accounts import get_or_create_user

router = APIRouter(prefix="/emails", tags=["emails"])

URGENCY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _email_to_brief(email: Email) -> EmailBrief:
    """Convert an Email ORM object to a brief response schema."""
    return EmailBrief(
        id=email.id,
        sender_email=email.sender_email,
        sender_name=email.sender_name,
        subject=email.subject,
        preview=email.preview,
        received_at=email.received_at,
        status=email.status,
        is_demo=email.is_demo,
        classification=AIClassificationOut.model_validate(email.classification) if email.classification else None,
        has_replies=len(email.replies) > 0,
        has_followup=any(fu.status == "pending" for fu in email.follow_ups),
    )


def _base_query(db: Session, user: User):
    """Start a query scoped to the user, eager-loading classification."""
    return (
        db.query(Email)
        .filter(Email.user_id == user.id)
        .outerjoin(AIClassification, Email.id == AIClassification.email_id)
    )


@router.get("", response_model=EmailListResponse)
def list_emails(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    urgency: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    follow_up: Optional[str] = Query(None, description="pending/completed/none"),
    sort: str = Query("newest", description="newest/oldest/urgency"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    user = get_or_create_user(db)
    query = _base_query(db, user)

    # Search
    if search:
        query = query.filter(or_(
            Email.subject.ilike(f"%{search}%"),
            Email.body_text.ilike(f"%{search}%"),
            Email.sender_email.ilike(f"%{search}%"),
            Email.sender_name.ilike(f"%{search}%"),
        ))

    # Category filter
    if category:
        query = query.filter(AIClassification.category == category)

    # Urgency filter
    if urgency:
        query = query.filter(AIClassification.urgency == urgency)

    # Status filter
    if status:
        query = query.filter(Email.status == status)

    # Follow-up filter
    if follow_up == "pending":
        query = query.filter(Email.follow_ups.any(FollowUp.status == "pending"))
    elif follow_up == "completed":
        query = query.filter(Email.follow_ups.any(FollowUp.status == "completed"))
    elif follow_up == "none":
        query = query.filter(~Email.follow_ups.any())

    # Count before pagination
    total = query.count()

    # Sorting
    if sort == "oldest":
        query = query.order_by(Email.received_at.asc())
    elif sort == "urgency":
        urgency_case = case(
            (AIClassification.urgency == "critical", 0),
            (AIClassification.urgency == "high", 1),
            (AIClassification.urgency == "medium", 2),
            (AIClassification.urgency == "low", 3),
            else_=4,
        )
        query = query.order_by(urgency_case.asc(), Email.received_at.desc())
    else:  # newest (default)
        query = query.order_by(Email.received_at.desc())

    # Paginate
    offset = (page - 1) * page_size
    emails = query.offset(offset).limit(page_size).all()

    briefs = [_email_to_brief(e) for e in emails]
    return EmailListResponse(emails=briefs, total=total, page=page, page_size=page_size)


@router.get("/{email_id}", response_model=EmailDetail)
def get_email(email_id: int, db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    email = db.query(Email).filter(
        Email.id == email_id, Email.user_id == user.id
    ).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")

    # Mark as read if unread
    if email.status == "unread":
        email.status = "read"
        db.commit()
        db.refresh(email)

    # Get thread emails (same thread_id, excluding self)
    thread = []
    if email.thread_id:
        thread_emails = db.query(Email).filter(
            Email.thread_id == email.thread_id,
            Email.id != email.id,
            Email.user_id == user.id
        ).order_by(Email.received_at.asc()).all()
        thread = [_email_to_brief(e) for e in thread_emails]

    return EmailDetail(
        id=email.id,
        sender_email=email.sender_email,
        sender_name=email.sender_name,
        recipient_email=email.recipient_email,
        subject=email.subject,
        body_text=email.body_text,
        body_html=email.body_html,
        preview=email.preview,
        received_at=email.received_at,
        status=email.status,
        is_demo=email.is_demo,
        responded_at=email.responded_at,
        classification=AIClassificationOut.model_validate(email.classification) if email.classification else None,
        replies=[ReplySuggestionOut.model_validate(r) for r in email.replies],
        follow_ups=[FollowUpBrief.model_validate(fu) for fu in email.follow_ups],
        thread=thread,
    )


@router.patch("/{email_id}/status", response_model=EmailBrief)
def update_email_status(email_id: int, payload: EmailStatusUpdate,
                        db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    email = db.query(Email).filter(
        Email.id == email_id, Email.user_id == user.id
    ).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")

    valid_statuses = ["unread", "read", "responded", "archived"]
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    email.status = payload.status
    if payload.status == "responded" and not email.responded_at:
        email.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(email)
    return _email_to_brief(email)


@router.patch("/{email_id}/classification", response_model=AIClassificationOut)
def update_classification(email_id: int, payload: ClassificationUpdate,
                          db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    email = db.query(Email).filter(
        Email.id == email_id, Email.user_id == user.id
    ).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")

    if not email.classification:
        raise HTTPException(status_code=400, detail="No classification to update.")

    original_category = email.classification.category
    original_urgency = email.classification.urgency

    if payload.category:
        email.classification.category = payload.category
    if payload.urgency:
        email.classification.urgency = payload.urgency
    email.classification.is_manual_override = True

    # Record feedback if changed
    if payload.category or payload.urgency:
        feedback = UserFeedback(
            email_id=email.id,
            original_category=original_category,
            corrected_category=payload.category or original_category,
            original_urgency=original_urgency,
            corrected_urgency=payload.urgency or original_urgency,
        )
        db.add(feedback)

    db.commit()
    db.refresh(email.classification)
    return AIClassificationOut.model_validate(email.classification)
