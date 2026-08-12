"""SMTP service for sending replies (optional feature, requires explicit confirmation)."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def send_reply(
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    to_email: str,
    subject: str,
    body: str,
    use_ssl: bool = True,
) -> Tuple[bool, str]:
    """Send a reply email via SMTP. Returns (success, message)."""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = username
        msg["To"] = to_email
        reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"
        msg["Subject"] = reply_subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=20)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=20)
            server.starttls()

        server.login(username, password)
        server.sendmail(username, [to_email], msg.as_string())
        server.quit()
        return True, "Reply sent successfully."
    except smtplib.SMTPAuthenticationError as e:
        return False, f"SMTP authentication failed: {e}"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {e}"
    except Exception as e:
        return False, f"Failed to send email: {e}"
