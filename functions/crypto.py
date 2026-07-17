"""Symmetric encryption for secrets at rest (no Streamlit, no I/O)."""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from functions.env import env

_PREFIX = "enc:v1:"


class CryptoError(ValueError):
    """Raised when encryption config or ciphertext is invalid."""


def _fernet() -> Fernet:
    key = env("CREDENTIALS_ENCRYPTION_KEY")
    if not key:
        raise CryptoError(
            "CREDENTIALS_ENCRYPTION_KEY is not set. "
            "Generate one with: python -c "
            '"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )
    try:
        return Fernet(key.encode("utf-8"))
    except (TypeError, ValueError) as exc:
        raise CryptoError(
            "CREDENTIALS_ENCRYPTION_KEY is invalid. "
            "It must be a Fernet key (url-safe base64, 32 bytes)."
        ) from exc


def encrypt_secret(plaintext: str) -> str:
    """Encrypt a secret for DB storage. Empty input stays empty."""
    value = (plaintext or "").strip()
    if not value:
        return ""
    if value.startswith(_PREFIX):
        return value
    token = _fernet().encrypt(value.encode("utf-8")).decode("utf-8")
    return f"{_PREFIX}{token}"


def decrypt_secret(stored: str) -> str:
    """Decrypt a stored secret. Legacy plaintext (no prefix) is returned as-is."""
    value = (stored or "").strip()
    if not value:
        return ""
    if not value.startswith(_PREFIX):
        return value
    ciphertext = value[len(_PREFIX) :]
    try:
        return _fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise CryptoError(
            "Could not decrypt stored credentials. "
            "Check CREDENTIALS_ENCRYPTION_KEY matches the key used to encrypt them."
        ) from exc


__all__ = ["CryptoError", "decrypt_secret", "encrypt_secret"]
