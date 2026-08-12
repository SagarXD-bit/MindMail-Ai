"""Fernet-based encryption for email account passwords."""

import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken

from .config import settings


def _get_fernet() -> Fernet:
    """Get a Fernet instance, deriving a key from settings or generating one."""
    key = settings.email_encryption_key
    if not key:
        # Derive a stable key from a random seed stored at import time.
        # This is a dev fallback — production should always set EMAIL_ENCRYPTION_KEY.
        key = base64.urlsafe_b64encode(
            hashlib.sha256(b"mailmind-dev-fallback-key").digest()
        ).decode()
    elif not key.endswith("="):
        # If the key isn't a valid Fernet key, derive one from it.
        key = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest()).decode()
    return Fernet(key.encode() if isinstance(key, str) else key)


_fernet = _get_fernet()


def encrypt_password(plaintext: str) -> str:
    """Encrypt a password and return a base64 string for storage."""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_password(ciphertext: str) -> str:
    """Decrypt a stored password. Returns empty string on failure."""
    try:
        return _fernet.decrypt(ciphertext.encode()).decode()
    except (InvalidToken, Exception):
        return ""
