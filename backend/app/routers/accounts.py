"""Email account router — IMAP configuration, connection testing, sync trigger."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import EmailAccount, Email, User, UserSettings
from ..schemas import EmailAccountCreate, EmailAccountOut, MessageResponse
from ..crypto import encrypt_password, decrypt_password
from ..imap_service import test_imap_connection, fetch_emails, IMAPResult
from ..ai_service import categorize_email
from ..seed_data import get_demo_emails

router = APIRouter(prefix="/accounts", tags=["accounts"])


def get_or_create_user(db: Session) -> User:
    """Get the single app user (single-tenant) or create a default."""
    user = db.query(User).first()
    if not user:
        user = User(name="MailMind User", email="user@mailmind.local")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("", response_model=list[EmailAccountOut])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(EmailAccount).all()


@router.post("", response_model=EmailAccountOut)
def create_account(payload: EmailAccountCreate, db: Session = Depends(get_db)):
    user = get_or_create_user(db)

    # Test the connection first
    success, message = test_imap_connection(
        payload.imap_server, payload.imap_port,
        payload.email_address, payload.password, payload.imap_ssl
    )

    # Create account record regardless (so user can see config), but set status
    account = EmailAccount(
        user_id=user.id,
        email_address=payload.email_address,
        imap_server=payload.imap_server,
        imap_port=payload.imap_port,
        imap_ssl=payload.imap_ssl,
        smtp_server=payload.smtp_server,
        smtp_port=payload.smtp_port,
        smtp_ssl=payload.smtp_ssl,
        encrypted_password=encrypt_password(payload.password),
        status="connected" if success else "error",
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    if not success:
        from fastapi import Response
        # Return 201 with the account, but include a warning header.
        # The frontend reads the response body for the account data.
        account.status = "error"
        db.commit()
        db.refresh(account)
        # Add X-Warning header so frontend can display it
        return JSONResponse(
            status_code=201,
            content={
                **EmailAccountOut.model_validate(account).model_dump(mode="json"),
                "warning": f"Account saved but connection test failed: {message}",
            },
            headers={"X-Warning": message},
        )

    return account


@router.delete("/{account_id}", response_model=MessageResponse)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Email account not found.")
    db.delete(account)
    db.commit()
    return MessageResponse(message="Account disconnected and removed.")


@router.post("/{account_id}/test", response_model=MessageResponse)
def test_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Email account not found.")

    password = decrypt_password(account.encrypted_password)
    if not password:
        raise HTTPException(status_code=400, detail="Could not decrypt stored password.")

    success, message = test_imap_connection(
        account.imap_server, account.imap_port,
        account.email_address, password, account.imap_ssl
    )
    account.status = "connected" if success else "error"
    db.commit()
    return MessageResponse(message=message, detail="connected" if success else "error")


# ---- SYNC ----

@router.post("/sync", response_model=dict)
def sync_emails(force_demo: bool = False, db: Session = Depends(get_db)):
    """Fetch new emails from IMAP or seed demo data."""
    from sqlalchemy import text as sql_text
    user = get_or_create_user(db)
    account = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()

    if account and not force_demo:
        # Real IMAP sync
        password = decrypt_password(account.encrypted_password)
        result = fetch_emails(
            account.imap_server, account.imap_port,
            account.email_address, password, account.imap_ssl, limit=20
        )
        if not result.success:
            # Fall back to demo if IMAP fails
            return _seed_demo_emails(db, user, account,
                                     error_msg=result.message)
        new_count = _process_fetched_emails(db, user, account, result.emails)
        account.status = "connected"
        account.last_sync_at = datetime.utcnow()
        db.commit()
        return {
            "status": "ok",
            "new_emails": new_count,
            "total_emails": db.query(Email).count(),
            "message": f"Synced {new_count} new email(s) from IMAP.",
            "mode": "imap",
        }

    # Demo mode
    return _seed_demo_emails(db, user, account)


def _process_fetched_emails(db: Session, user: User, account: EmailAccount,
                            fetched: list) -> int:
    """Process and store fetched IMAP emails. Returns count of new emails."""
    new_count = 0
    for item in fetched:
        # Dedup by message_id
        if item.get("message_id"):
            existing = db.query(Email).filter(
                Email.message_id == item["message_id"]
            ).first()
            if existing:
                continue

        email_obj = Email(
            user_id=user.id,
            account_id=account.id,
            message_id=item.get("message_id"),
            thread_id=item.get("thread_id"),
            sender_email=item["sender_email"],
            sender_name=item.get("sender_name"),
            recipient_email=item["recipient_email"],
            subject=item["subject"],
            body_text=item.get("body_text", ""),
            body_html=item.get("body_html"),
            preview=item.get("preview", ""),
            received_at=item.get("received_at", datetime.utcnow()),
            status="unread",
            is_demo=False,
        )
        db.add(email_obj)
        db.flush()

        # AI categorize
        classification = categorize_email(
            email_obj.subject, email_obj.body_text or "", email_obj.sender_email
        )
        from ..models import AIClassification
        ai_cls = AIClassification(
            email_id=email_obj.id,
            category=classification.category,
            urgency=classification.urgency,
            confidence=classification.confidence,
            explanation=classification.explanation,
            needs_response=classification.needs_response,
            suggested_followup=classification.suggested_followup,
        )
        db.add(ai_cls)
        new_count += 1

    db.commit()
    return new_count


def _seed_demo_emails(db: Session, user: User, account=None,
                      error_msg: str = None) -> dict:
    """Seed demo emails if none exist yet."""
    from ..models import AIClassification
    demo_data = get_demo_emails()

    # Check if demo emails already exist
    existing_demo = db.query(Email).filter(Email.is_demo == True).count()
    if existing_demo > 0:
        total = db.query(Email).count()
        return {
            "status": "ok",
            "new_emails": 0,
            "total_emails": total,
            "message": f"Demo data already loaded ({total} emails). Use refresh to re-sync." +
                       (f" IMAP error: {error_msg}" if error_msg else ""),
            "mode": "demo",
        }

    new_count = 0
    for item in demo_data:
        email_obj = Email(
            user_id=user.id,
            account_id=account.id if account else None,
            message_id=f"demo-{new_count}-{item['sender_email']}",
            sender_email=item["sender_email"],
            sender_name=item.get("sender_name"),
            recipient_email=user.email,
            subject=item["subject"],
            body_text=item["body_text"],
            preview=item["body_text"][:200].replace("\n", " ").strip(),
            received_at=item["received_at"],
            status="unread",
            is_demo=True,
        )
        db.add(email_obj)
        db.flush()

        ai_cls = AIClassification(
            email_id=email_obj.id,
            category=item["category"],
            urgency=item["urgency"],
            confidence=item["confidence"],
            explanation=item["explanation"],
            needs_response=item.get("needs_response", False),
            suggested_followup=item.get("suggested_followup", False),
        )
        db.add(ai_cls)
        new_count += 1

    db.commit()
    total = db.query(Email).count()
    return {
        "status": "ok",
        "new_emails": new_count,
        "total_emails": total,
        "message": f"Loaded {new_count} demo emails. AI categorization applied." +
                   (f" (IMAP sync failed: {error_msg})" if error_msg else ""),
        "mode": "demo",
    }
