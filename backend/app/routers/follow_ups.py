"""Follow-ups router — create, list, complete, snooze, delete."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import FollowUp, Email, User
from ..schemas import FollowUpCreate, FollowUpUpdate, FollowUpOut, EmailBrief
from .accounts import get_or_create_user
from .emails import _email_to_brief

router = APIRouter(prefix="/follow-ups", tags=["follow-ups"])


@router.get("", response_model=list[FollowUpOut])
def list_follow_ups(
    status: Optional[str] = Query(None, description="pending/completed/snoozed/overdue/upcoming"),
    db: Session = Depends(get_db),
):
    user = get_or_create_user(db)
    now = datetime.utcnow()
    query = db.query(FollowUp).filter(FollowUp.user_id == user.id)

    if status == "overdue":
        query = query.filter(FollowUp.status == "pending", FollowUp.reminder_at < now)
    elif status == "upcoming":
        query = query.filter(FollowUp.status == "pending", FollowUp.reminder_at >= now)
    elif status == "pending":
        query = query.filter(FollowUp.status == "pending")
    elif status == "completed":
        query = query.filter(FollowUp.status == "completed")
    elif status == "snoozed":
        query = query.filter(FollowUp.status == "snoozed")

    follow_ups = query.order_by(FollowUp.reminder_at.asc()).all()

    result = []
    for fu in follow_ups:
        out = FollowUpOut.model_validate(fu)
        out.email = _email_to_brief(fu.email)
        result.append(out)
    return result


@router.post("", response_model=FollowUpOut)
def create_follow_up(payload: FollowUpCreate, db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    email = db.query(Email).filter(
        Email.id == payload.email_id, Email.user_id == user.id
    ).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")

    follow_up = FollowUp(
        user_id=user.id,
        email_id=payload.email_id,
        reminder_at=payload.reminder_at,
        note=payload.note,
        status="pending",
    )
    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)

    out = FollowUpOut.model_validate(follow_up)
    out.email = _email_to_brief(follow_up.email)
    return out


@router.patch("/{follow_up_id}", response_model=FollowUpOut)
def update_follow_up(follow_up_id: int, payload: FollowUpUpdate,
                     db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    follow_up = db.query(FollowUp).filter(
        FollowUp.id == follow_up_id, FollowUp.user_id == user.id
    ).first()
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found.")

    if payload.reminder_at is not None:
        follow_up.reminder_at = payload.reminder_at
    if payload.note is not None:
        follow_up.note = payload.note
    if payload.status is not None:
        valid_statuses = ["pending", "completed", "snoozed"]
        if payload.status not in valid_statuses:
            raise HTTPException(status_code=400,
                                detail=f"Invalid status. Must be one of: {valid_statuses}")
        follow_up.status = payload.status
        if payload.status == "completed":
            follow_up.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(follow_up)

    out = FollowUpOut.model_validate(follow_up)
    out.email = _email_to_brief(follow_up.email)
    return out


@router.delete("/{follow_up_id}")
def delete_follow_up(follow_up_id: int, db: Session = Depends(get_db)):
    user = get_or_create_user(db)
    follow_up = db.query(FollowUp).filter(
        FollowUp.id == follow_up_id, FollowUp.user_id == user.id
    ).first()
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found.")

    db.delete(follow_up)
    db.commit()
    return {"message": "Follow-up deleted."}
