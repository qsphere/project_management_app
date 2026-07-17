"""Password hashing and auth field validation (no Streamlit, no I/O)."""

from __future__ import annotations

import hashlib
import re
import secrets

_PBKDF2_ROUNDS = 100_000
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LEN = 8


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        _PBKDF2_ROUNDS,
    )
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        _PBKDF2_ROUNDS,
    )
    return secrets.compare_digest(check.hex(), digest)


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def validate_sign_in(email: str, password: str) -> str | None:
    if not normalize_email(email):
        return "Email address is required."
    if not _EMAIL_RE.match(normalize_email(email)):
        return "Enter a valid email address."
    if not (password or "").strip():
        return "Password is required."
    return None


def validate_create_account(full_name: str, email: str, password: str) -> str | None:
    if not (full_name or "").strip():
        return "Full name is required."
    err = validate_sign_in(email, password)
    if err:
        return err
    if len(password) < MIN_PASSWORD_LEN:
        return f"Password must be at least {MIN_PASSWORD_LEN} characters."
    return None
