"""Replies router — AI reply generation, edit, mark used/discard, and send via SMTP."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Email, ReplySuggestion, EmailAccount, User, UserSettings
from ..schemas import (
    ReplyGenerate, ReplyUpdate, ReplySuggestionOut, SendReplyRequest,
    EmailBrief, MessageResponse, AIClassificationOut
)
from ..ai_service import generate_reply
from ..crypto import decrypt_password
from ..smtp_service import send_reply
from .accounts import get_or_create_user
from .emails import _email_to_brief

router = APIRouter(tags=["replies"])


@router.post("/emails/{email_id}/replies", response_model=ReplySuggestionOut)
def generate_email_reply(email_id: int, payload: ReplyGenerate,
                         db: Session = Depends(get_db)):
    """Generate an AI reply suggestion for an email in the requested tone."""
    user = get_or_create_user(db)
    email = db.query(Email).filter(
        Email.id == email_id, Email.user_id == user.id
    ).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")

    valid_tones = ["professional", "friendly", "concise"]
    if payload.tone not in valid_tones:
        raise HTTPException(status_code=400,
                            detail=f"Invalid tone. Must be one of: {valid_tones}")

    content = generate_reply(
        subject=email.subject,
        body=email.body_text or "",
        sender_name=email.sender_name or email.sender_email,
        tone=payload.tone,
    )

    if not content:
        raise HTTPException(status_code=500, detail="Could not generate a reply. Please try again.")

    reply = ReplySuggestion(
        email_id=email.id,
        tone=payload.tone,
        content=content,
        status="draft",
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return ReplySuggestionOut.model_validate(reply)


@router.patch("/emails/{email_id}/replies/{reply_id}", response_model=ReplySuggestionOut)
def update_reply(email_id: int, reply_id: int, payload: ReplyUpdate,
                 db: Session = Depends(get_db)):
    """Edit reply content or change status (used/discard)."""
    user = get_or_create_user(db)
    reply = db.query(ReplySuggestion).join(Email).filter(
        ReplySuggestion.id == reply_id,
        ReplySuggestion.email_id == email_id,
        Email.user_id == user.id,
    ).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found.")

    if payload.content is not None:
        reply.content = payload.content
    if payload.status is not None:
        valid_statuses = ["draft", "used", "discarded"]
        if payload.status not in valid_statuses:
            raise HTTPException(status_code=400,
                                detail=f"Invalid status. Must be one of: {valid_statuses}")
        reply.status = payload.status

    db.commit()
    db.refresh(reply)
    return ReplySuggestionOut.model_validate(reply)


@router.post("/emails/{email_id}/send", response_model=EmailBrief)
def send_email_reply(email_id: int, payload: SendReplyRequest,
                     db: Session = Depends(get_db)):
    """Send a reply via SMTP. Requires explicit confirmation."""
    user = get_or_create_user(db)
    email = db.query(Email).filter(
        Email.id == email_id, Email.user_id == user.id
    ).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")

    if not payload.confirm:
        raise HTTPException(status_code=400,
                            detail="Confirmation required. Set 'confirm' to true to send.")

    reply = db.query(ReplySuggestion).filter(
        ReplySuggestion.id == payload.reply_id,
        ReplySuggestion.email_id == email.id,
    ).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found.")

    # Find the email account for SMTP credentials
    account = db.query(EmailAccount).filter(
        EmailAccount.user_id == user.id
    ).first()

    if not account or not account.smtp_server:
        # No SMTP configured — mark as sent/used (demo mode behavior)
        reply.status = "used"
        email.status = "responded"
        email.responded_at = datetime.utcnow()
        db.commit()
        db.refresh(email)
        # Return the email brief directly with a success response
        return _email_to_brief(email)

    # Real SMTP send
    password = decrypt_password(account.encrypted_password)
    success, message = send_reply(
        smtp_server=account.smtp_server,
        smtp_port=account.smtp_port or 587,
        username=account.email_address,
        password=password,
        to_email=email.sender_email,
        subject=email.subject,
        body=reply.content,
        use_ssl=account.smtp_ssl,
    )

    if not success:
        raise HTTPException(status_code=502, detail=f"Failed to send email: {message}")

    reply.status = "used"
    email.status = "responded"
    email.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(email)
    return _email_to_brief(email)
