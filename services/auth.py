"""Auth orchestration over Neon users (no Streamlit, no raw SQL)."""

from __future__ import annotations

from typing import Any

from clients import NeonClient
from functions.auth import (
    hash_password,
    normalize_email,
    validate_create_account,
    validate_sign_in,
    verify_password,
)
from services.neon import connected_neon_client


class AuthError(Exception):
    """User-facing auth failure."""


def _client() -> NeonClient:
    client = connected_neon_client()
    if client is None:
        raise AuthError(
            "Database is not configured. Set DATABASE_URL in .env to enable accounts."
        )
    client.ensure_users_table()
    return client


def _public_user(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
    }


def create_account(
    *, full_name: str, email: str, password: str
) -> dict[str, Any]:
    err = validate_create_account(full_name, email, password)
    if err:
        raise AuthError(err)
    client = _client()
    email_norm = normalize_email(email)
    if client.get_user_by_email(email_norm) is not None:
        raise AuthError("An account with this email already exists.")
    row = client.create_user(
        full_name=full_name.strip(),
        email=email_norm,
        password_hash=hash_password(password),
    )
    return _public_user(row)


def sign_in(*, email: str, password: str) -> dict[str, Any]:
    err = validate_sign_in(email, password)
    if err:
        raise AuthError(err)
    client = _client()
    row = client.get_user_by_email(normalize_email(email))
    if row is None or not verify_password(password, row["password_hash"]):
        raise AuthError("Invalid email or password.")
    return _public_user(row)


__all__ = ["AuthError", "create_account", "sign_in"]