"""Encryption-at-rest for PII fields (LLD §7). Stand-in for an HSM-backed
AES-256 key management service: a Fernet key (itself AES-128-CBC + HMAC)
supplied via ENCRYPTION_KEY. Swapping to real KMS/HSM later means changing
how `_fernet` obtains its key, not the call sites.
"""
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


def _pad_key(raw: str) -> bytes:
    # Fernet requires a 32-byte urlsafe-base64 key. If the configured value
    # isn't already valid, derive a stable one so local/dev setups don't
    # have to hand-generate a key.
    try:
        Fernet(raw.encode())
        return raw.encode()
    except Exception:
        import base64
        import hashlib

        digest = hashlib.sha256(raw.encode()).digest()
        return base64.urlsafe_b64encode(digest)


_fernet = Fernet(_pad_key(settings.encryption_key))


def encrypt_value(value: str | None) -> str | None:
    if value is None:
        return None
    return _fernet.encrypt(value.encode()).decode()


def decrypt_value(token: str | None) -> str | None:
    if token is None:
        return None
    try:
        return _fernet.decrypt(token.encode()).decode()
    except InvalidToken:
        # Value was never encrypted (e.g. seeded/legacy plaintext) - return as-is.
        return token
