"""Resend email client — sole place for Resend API calls."""

from __future__ import annotations

from typing import Any

import resend


class ResendClient:
    """Thin wrapper around the Resend SDK. All Resend I/O goes through here."""

    def __init__(self, api_key: str, *, from_email: str):
        if not (api_key or "").strip():
            raise ValueError("RESEND_API_KEY is required")
        if not (from_email or "").strip():
            raise ValueError("RESEND_FROM_EMAIL is required")
        self._api_key = api_key.strip()
        self._from_email = from_email.strip()

    def send_email(
        self,
        *,
        to: str,
        subject: str,
        html: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        """Send one email. Raises ``resend.exceptions.ResendError`` on failure."""
        resend.api_key = self._api_key
        return resend.Emails.send(
            {
                "from": self._from_email,
                "to": [to],
                "subject": subject,
                "html": html,
            },
            {"idempotency_key": idempotency_key},
        )


__all__ = ["ResendClient"]
