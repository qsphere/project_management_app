"""Email orchestration over ``clients.ResendClient`` (no raw Resend I/O)."""

from __future__ import annotations

import logging
from html import escape

from clients import ResendClient
from functions.env import env

logger = logging.getLogger(__name__)

_DEFAULT_FROM = "Project Management <onboarding@resend.dev>"


def connected_resend_client(
    api_key: str | None = None,
    *,
    from_email: str | None = None,
) -> ResendClient | None:
    """Build a client from env; None if ``RESEND_API_KEY`` is unset."""
    key = (api_key if api_key is not None else env("RESEND_API_KEY")).strip()
    if not key:
        return None
    sender = (
        from_email
        if from_email is not None
        else env("RESEND_FROM_EMAIL") or _DEFAULT_FROM
    ).strip()
    return ResendClient(key, from_email=sender)


def send_welcome_email(*, user_id: int | str, full_name: str, email: str) -> None:
    """Send a welcome email after account creation. No-op if Resend is unset."""
    client = connected_resend_client()
    if client is None:
        logger.warning(
            "Skipping welcome email: set RESEND_API_KEY in .env to enable email."
        )
        return
    name = escape((full_name or "").strip() or "there")
    html = (
        f"<p>Hi {name},</p>"
        "<p>Your account was created successfully. "
        "You can sign in anytime with this email address.</p>"
        "<p>— Project Management</p>"
    )
    try:
        client.send_email(
            to=email,
            subject="Welcome — your account is ready",
            html=html,
            idempotency_key=f"welcome-email/{user_id}",
        )
    except Exception:
        logger.exception("Failed to send welcome email to %s", email)


def send_account_deleted_email(
    *, user_id: int | str, full_name: str, email: str
) -> None:
    """Send confirmation after account deletion. No-op if Resend is unset."""
    client = connected_resend_client()
    if client is None:
        logger.warning(
            "Skipping account-deleted email: set RESEND_API_KEY in .env "
            "to enable email."
        )
        return
    name = escape((full_name or "").strip() or "there")
    html = (
        f"<p>Hi {name},</p>"
        "<p>Your account has been permanently deleted. "
        "If you did not request this, contact support.</p>"
        "<p>— Project Management</p>"
    )
    try:
        client.send_email(
            to=email,
            subject="Your account has been deleted",
            html=html,
            idempotency_key=f"account-deleted-email/{user_id}",
        )
    except Exception:
        logger.exception("Failed to send account-deleted email to %s", email)


__all__ = [
    "connected_resend_client",
    "send_account_deleted_email",
    "send_welcome_email",
]
