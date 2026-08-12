"""Tests for demo mode sync and IMAP error handling.

Verifies:
1. Demo sync works cleanly with no account (no IMAP attempt).
2. Demo sync with an errored account doesn't attempt IMAP.
3. force_demo=True always goes to demo mode even with a connected account.
4. Demo sync messages never contain raw OS error strings like [Errno -2].
5. _friendly_imap_error produces user-friendly messages.
6. Real IMAP sync path is used when account.status == "connected".
"""

import socket
import imaplib
import pytest
from unittest.mock import patch, MagicMock

from app.models import User, EmailAccount, Email
from app.routers.accounts import sync_emails, _seed_demo_emails, get_or_create_user
from app.imap_service import _friendly_imap_error


# ─── 1. Demo sync with no account ─────────────────────────────────────────

class TestDemoSyncNoAccount:
    """Demo mode should work when no email account is configured."""

    def test_sync_no_account_seeds_demo(self, db_session):
        """Sync with no account should seed demo data cleanly."""
        user = db_session.query(User).first()
        result = sync_emails(db=db_session)
        assert result["mode"] == "demo"
        assert result["status"] == "ok"
        assert result["new_emails"] > 0
        assert "demo" in result["message"].lower()

    def test_sync_no_account_already_seeded(self, seeded_db):
        """Re-sync with no account should say demo data already loaded."""
        result = sync_emails(db=seeded_db)
        assert result["mode"] == "demo"
        assert result["new_emails"] == 0
        assert "already loaded" in result["message"].lower()

    def test_sync_no_account_no_raw_error(self, seeded_db):
        """Demo sync message must NOT contain raw OS error strings."""
        result = sync_emails(db=seeded_db)
        assert "[Errno" not in result["message"]
        assert "Name or service not known" not in result["message"]
        assert "IMAP error" not in result["message"]


# ─── 2. Sync with errored account ──────────────────────────────────────────

class TestSyncErroredAccount:
    """Sync should NOT attempt IMAP when account status is 'error'."""

    def test_sync_errored_account_goes_to_demo(self, seeded_db):
        """An account with status='error' should not attempt IMAP."""
        user = seeded_db.query(User).first()
        account = EmailAccount(
            user_id=user.id,
            email_address="test@example.com",
            imap_server="nonexistent.invalid",
            imap_port=993,
            imap_ssl=True,
            encrypted_password="dummy",
            status="error",
        )
        seeded_db.add(account)
        seeded_db.commit()

        result = sync_emails(db=seeded_db)
        assert result["mode"] == "demo"
        assert result["status"] == "ok"

    def test_sync_errored_account_no_raw_error(self, seeded_db):
        """Message should NOT contain raw OS error even with errored account."""
        user = seeded_db.query(User).first()
        account = EmailAccount(
            user_id=user.id,
            email_address="test@example.com",
            imap_server="nonexistent.invalid",
            imap_port=993,
            imap_ssl=True,
            encrypted_password="dummy",
            status="error",
        )
        seeded_db.add(account)
        seeded_db.commit()

        result = sync_emails(db=seeded_db)
        assert "[Errno" not in result["message"]
        assert "Name or service not known" not in result["message"]

    def test_sync_errored_account_friendly_message(self, seeded_db):
        """Message should guide user to Settings to fix the account."""
        user = seeded_db.query(User).first()
        account = EmailAccount(
            user_id=user.id,
            email_address="test@example.com",
            imap_server="nonexistent.invalid",
            imap_port=993,
            imap_ssl=True,
            encrypted_password="dummy",
            status="error",
        )
        seeded_db.add(account)
        seeded_db.commit()

        result = sync_emails(db=seeded_db)
        assert "Settings" in result["message"] or "Demo mode" in result["message"]


# ─── 3. force_demo=True ────────────────────────────────────────────────────

class TestForceDemo:
    """force_demo should always go to demo mode."""

    def test_force_demo_with_connected_account(self, seeded_db):
        """force_demo=True should skip IMAP even with a connected account."""
        user = seeded_db.query(User).first()
        account = EmailAccount(
            user_id=user.id,
            email_address="real@gmail.com",
            imap_server="imap.gmail.com",
            imap_port=993,
            imap_ssl=True,
            encrypted_password="dummy",
            status="connected",
        )
        seeded_db.add(account)
        seeded_db.commit()

        result = sync_emails(force_demo=True, db=seeded_db)
        assert result["mode"] == "demo"
        assert result["status"] == "ok"


# ─── 4. Connected account attempts IMAP ────────────────────────────────────

class TestConnectedAccountSync:
    """A validated connected account should attempt real IMAP sync."""

    def test_connected_account_attempts_imap(self, seeded_db):
        """When account status='connected', sync should try IMAP."""
        user = seeded_db.query(User).first()
        account = EmailAccount(
            user_id=user.id,
            email_address="real@gmail.com",
            imap_server="imap.gmail.com",
            imap_port=993,
            imap_ssl=True,
            encrypted_password="dummy_encrypted",
            status="connected",
        )
        seeded_db.add(account)
        seeded_db.commit()

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.emails = []
        mock_result.message = "Fetched 0 emails."
        mock_result.count = 0

        with patch("app.routers.accounts.fetch_emails", return_value=mock_result):
            result = sync_emails(db=seeded_db)

        assert result["mode"] == "imap"
        assert result["status"] == "ok"

    def test_connected_account_imap_failure_returns_demo(self, seeded_db):
        """If IMAP fails on a connected account, fall back to demo gracefully."""
        user = seeded_db.query(User).first()
        account = EmailAccount(
            user_id=user.id,
            email_address="real@gmail.com",
            imap_server="imap.gmail.com",
            imap_port=993,
            imap_ssl=True,
            encrypted_password="dummy_encrypted",
            status="connected",
        )
        seeded_db.add(account)
        seeded_db.commit()

        mock_result = MagicMock()
        mock_result.success = False
        mock_result.emails = []
        mock_result.message = "Connection timed out"

        with patch("app.routers.accounts.fetch_emails", return_value=mock_result):
            result = sync_emails(db=seeded_db)

        assert result["mode"] == "demo"
        assert result["status"] == "ok"
        assert "[Errno" not in result["message"]
        assert "Name or service not known" not in result["message"]


# ─── 5. IMAP error message friendliness ────────────────────────────────────

class TestFriendlyIMAPError:
    """_friendly_imap_error should produce user-friendly messages."""

    def test_dns_failure_no_errno(self):
        err = socket.gaierror("[Errno -2] Name or service not known")
        msg = _friendly_imap_error(err)
        assert "Errno" not in msg
        assert "Name or service not known" not in msg
        assert "IMAP server hostname" in msg or "server address" in msg.lower()

    def test_connection_refused(self):
        err = ConnectionRefusedError("[Errno 111] Connection refused")
        msg = _friendly_imap_error(err)
        assert "Errno" not in msg
        assert "refused" in msg.lower() or "port" in msg.lower()

    def test_timeout(self):
        err = TimeoutError("timed out")
        msg = _friendly_imap_error(err)
        assert "timed out" in msg.lower()
        assert "Errno" not in msg

    def test_imap_auth_error(self):
        err = imaplib.IMAP4.error("authentication failed")
        msg = _friendly_imap_error(err)
        assert "Authentication failed" in msg or "app password" in msg.lower()

    def test_generic_oserror(self):
        err = OSError("network unreachable")
        msg = _friendly_imap_error(err)
        assert "unable to reach" in msg.lower() or "network" in msg.lower()
