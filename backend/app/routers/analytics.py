"""Analytics router — aggregated response metrics, distributions, and trends."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from ..database import get_db
from ..models import (
    Email, AIClassification, FollowUp, ReplySuggestion, UserFeedback, User
)
from ..schemas import AnalyticsResponse
from .accounts import get_or_create_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    now = datetime.utcnow()

    # Base query for this user's emails
    all_emails = db.query(Email).filter(Email.user_id == user.id)
    total_emails = all_emails.count()

    # Emails by category
    category_rows = (
        db.query(AIClassification.category, func.count(Email.id))
        .join(Email, Email.id == AIClassification.email_id)
        .filter(Email.user_id == user.id)
        .group_by(AIClassification.category)
        .all()
    )
    emails_by_category = {cat: count for cat, count in category_rows}

    # Emails by urgency
    urgency_rows = (
        db.query(AIClassification.urgency, func.count(Email.id))
        .join(Email, Email.id == AIClassification.email_id)
        .filter(Email.user_id == user.id)
        .group_by(AIClassification.urgency)
        .all()
    )
    emails_by_urgency = {urg: count for urg, count in urgency_rows}

    # Response metrics
    needs_response_count = (
        db.query(AIClassification)
        .join(Email, Email.id == AIClassification.email_id)
        .filter(Email.user_id == user.id, AIClassification.needs_response == True)
        .count()
    )
    emails_responded = all_emails.filter(Email.status == "responded").count()
    pending_responses = needs_response_count - emails_responded
    if pending_responses < 0:
        pending_responses = 0

    # Average response time
    responded_emails = all_emails.filter(
        Email.status == "responded", Email.responded_at.isnot(None)
    ).all()
    avg_response_time_hours = None
    if responded_emails:
        total_hours = sum(
            (e.responded_at - e.received_at).total_seconds() / 3600
            for e in responded_emails
        )
        avg_response_time_hours = round(total_hours / len(responded_emails), 1)

    # Follow-up metrics
    all_follow_ups = db.query(FollowUp).filter(FollowUp.user_id == user.id)
    follow_ups_completed = all_follow_ups.filter(FollowUp.status == "completed").count()
    follow_ups_overdue = all_follow_ups.filter(
        FollowUp.status == "pending", FollowUp.reminder_at < now
    ).count()
    follow_ups_upcoming = all_follow_ups.filter(
        FollowUp.status == "pending", FollowUp.reminder_at >= now
    ).count()

    # AI accuracy: % of classifications NOT manually corrected
    total_classified = (
        db.query(AIClassification)
        .join(Email, Email.id == AIClassification.email_id)
        .filter(Email.user_id == user.id)
        .count()
    )
    feedback_count = (
        db.query(UserFeedback)
        .join(Email, Email.id == UserFeedback.email_id)
        .filter(Email.user_id == user.id)
        .count()
    )
    ai_accuracy = 0.0
    if total_classified > 0:
        ai_accuracy = round((1 - feedback_count / total_classified) * 100, 1)

    # Reply metrics
    all_replies = db.query(ReplySuggestion).join(Email).filter(Email.user_id == user.id)
    reply_generated = all_replies.count()
    reply_used = all_replies.filter(ReplySuggestion.status == "used").count()

    # Response rate
    response_rate = 0.0
    if needs_response_count > 0:
        response_rate = round((emails_responded / needs_response_count) * 100, 1)

    # Recent trend (last 14 days)
    fourteen_days_ago = now - timedelta(days=14)
    trend_rows = (
        db.query(
            func.date(Email.received_at).label("date"),
            func.count(Email.id).label("count"),
        )
        .filter(Email.user_id == user.id, Email.received_at >= fourteen_days_ago)
        .group_by(func.date(Email.received_at))
        .order_by(func.date(Email.received_at).asc())
        .all()
    )
    recent_trend = [{"date": str(row.date), "count": row.count} for row in trend_rows]

    return AnalyticsResponse(
        total_emails=total_emails,
        emails_by_category=emails_by_category,
        emails_by_urgency=emails_by_urgency,
        emails_requiring_response=needs_response_count,
        emails_responded_to=emails_responded,
        pending_responses=pending_responses,
        avg_response_time_hours=avg_response_time_hours,
        follow_ups_completed=follow_ups_completed,
        follow_ups_overdue=follow_ups_overdue,
        follow_ups_upcoming=follow_ups_upcoming,
        ai_accuracy=ai_accuracy,
        reply_suggestions_generated=reply_generated,
        reply_suggestions_used=reply_used,
        response_rate=response_rate,
        recent_trend=recent_trend,
    )
