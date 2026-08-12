"""IMAP email fetching and parsing service."""

import imaplib
import email
from email.header import decode_header
from datetime import datetime
from typing import List, Optional, Tuple
import logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def _decode_str(s) -> str:
    """Decode an email header string."""
    if s is None:
        return ""
    parts = decode_header(s)
    result = []
    for text, charset in parts:
        if isinstance(text, bytes):
            try:
                result.append(text.decode(charset or "utf-8", errors="replace"))
            except (LookupError, Exception):
                result.append(text.decode("utf-8", errors="replace"))
        else:
            result.append(str(text))
    return "".join(result)


def _extract_email_address(from_header: str) -> Tuple[str, str]:
    """Extract email address and name from a From header."""
    if not from_header:
        return ("unknown@unknown.com", "")
    decoded = _decode_str(from_header)
    # Pattern: "Name" <email@addr.com> or Name <email@addr.com> or email@addr.com
    if "<" in decoded and ">" in decoded:
        name_part = decoded[:decoded.rfind("<")].strip().strip('"').strip()
        email_part = decoded[decoded.rfind("<") + 1:decoded.rfind(">")].strip()
        return (email_part, name_part)
    else:
        return (decoded.strip(), "")


def _html_to_text(html: str) -> str:
    """Convert HTML to plain text."""
    soup = BeautifulSoup(html, "html.parser")
    # Remove script and style elements
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    # Collapse multiple newlines
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _get_body(msg) -> Tuple[Optional[str], Optional[str]]:
    """Extract plain text and HTML bodies from an email message."""
    text_body = None
    html_body = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))
            if "attachment" in disposition.lower():
                continue
            if content_type == "text/plain" and text_body is None:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        text_body = payload.decode(charset, errors="replace")
                    except (LookupError, Exception):
                        text_body = payload.decode("utf-8", errors="replace")
            elif content_type == "text/html" and html_body is None:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        html_body = payload.decode(charset, errors="replace")
                    except (LookupError, Exception):
                        html_body = payload.decode("utf-8", errors="replace")
    else:
        content_type = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            try:
                decoded = payload.decode(charset, errors="replace")
            except (LookupError, Exception):
                decoded = payload.decode("utf-8", errors="replace")
            if content_type == "text/plain":
                text_body = decoded
            elif content_type == "text/html":
                html_body = decoded

    # If only HTML, convert to text
    if text_body is None and html_body is not None:
        text_body = _html_to_text(html_body)
    # If only text, no html
    return text_body, html_body


class IMAPResult:
    def __init__(self, success: bool, message: str, emails: list = None, count: int = 0):
        self.success = success
        self.message = message
        self.emails = emails or []
        # emails is a list of dicts: {message_id, sender_email, sender_name,
        #   recipient_email, subject, body_text, body_html, preview, received_at, thread_id}
        self.count = count


def test_imap_connection(server: str, port: int, email_addr: str, password: str,
                         use_ssl: bool = True) -> Tuple[bool, str]:
    """Test an IMAP connection. Returns (success, message)."""
    try:
        if use_ssl:
            conn = imaplib.IMAP4_SSL(server, port, timeout=15)
        else:
            conn = imaplib.IMAP4(server, port, timeout=15)
        conn.login(email_addr, password)
        conn.logout()
        return True, "Connection successful."
    except imaplib.IMAP4.error as e:
        return False, f"IMAP authentication failed: {e}"
    except TimeoutError as e:
        return False, f"Connection timed out or unreachable: {e}"
    except OSError as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"Connection failed: {e}"


def fetch_emails(server: str, port: int, email_addr: str, password: str,
                 use_ssl: bool = True, limit: int = 20,
                 folder: str = "INBOX") -> IMAPResult:
    """Fetch recent emails from an IMAP server.

    Returns IMAPResult with parsed emails or error info.
    """
    conn = None
    try:
        if use_ssl:
            conn = imaplib.IMAP4_SSL(server, port, timeout=20)
        else:
            conn = imaplib.IMAP4(server, port, timeout=20)
        conn.login(email_addr, password)
        conn.select(folder, readonly=True)

        # Search for all emails, then fetch the most recent `limit`
        status, data = conn.search(None, "ALL")
        if status != "OK":
            return IMAPResult(False, f"Failed to search mailbox: status={status}")

        ids = data[0].split()
        if not ids:
            return IMAPResult(True, "Mailbox is empty.", [], 0)

        # Take the most recent `limit` emails
        recent_ids = ids[-limit:] if len(ids) > limit else ids

        emails = []
        for eid in reversed(recent_ids):
            status, msg_data = conn.fetch(eid, "(RFC822)")
            if status != "OK" or not msg_data or not msg_data[0]:
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            sender_email, sender_name = _extract_email_address(msg.get("From", ""))
            subject = _decode_str(msg.get("Subject", "(No Subject)"))
            message_id = msg.get("Message-ID", "")
            recipient = _decode_str(msg.get("To", email_addr))
            # Also extract from Delivered-To or envelope
            if not recipient or "@" not in recipient:
                recipient = _decode_str(msg.get("Delivered-To", email_addr))

            body_text, body_html = _get_body(msg)
            if body_text is None:
                body_text = ""

            # Parse date
            date_str = msg.get("Date", "")
            received_at = _parse_date(date_str)

            # Thread ID from References or In-Reply-To
            thread_id = msg.get("References", "") or msg.get("In-Reply-To", "")

            preview = (body_text or "")[:200].replace("\n", " ").strip()

            emails.append({
                "message_id": message_id,
                "sender_email": sender_email,
                "sender_name": sender_name,
                "recipient_email": recipient,
                "subject": subject,
                "body_text": body_text,
                "body_html": html_body,
                "preview": preview[:200],
                "received_at": received_at,
                "thread_id": thread_id[:500] if thread_id else None,
            })

        conn.logout()
        return IMAPResult(True, f"Fetched {len(emails)} emails.", emails, len(emails))

    except imaplib.IMAP4.error as e:
        return IMAPResult(False, f"IMAP error: {e}")
    except TimeoutError as e:
        return IMAPResult(False, f"Connection error: {e}")
    except OSError as e:
        return IMAPResult(False, f"Connection error: {e}")
    except Exception as e:
        return IMAPResult(False, f"Failed to fetch emails: {e}")
    finally:
        if conn:
            try:
                conn.logout()
            except Exception:
                pass


def _parse_date(date_str: str) -> datetime:
    """Parse an email Date header into a datetime."""
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return datetime.utcnow()
