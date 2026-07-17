from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

import pandas as pd


def format_card_date(value: str | None) -> str:
    if not value:
        return ""
    # Trello returns ISO timestamps; show the date portion for editing convenience.
    return value[:10] if len(value) >= 10 else value


def parse_card_date(value: str | None) -> date | None:
    raw = format_card_date(value)
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def display_card_date(value: str | None) -> str:
    parsed = parse_card_date(value)
    if parsed is None:
        return "—"
    return parsed.strftime("%b %d, %Y").replace(" 0", " ")


def format_target(iso_date: str | None) -> str:
    if not iso_date:
        return "No target date"
    try:
        return datetime.strptime(iso_date[:10], "%Y-%m-%d").strftime("Target %b %d")
    except ValueError:
        return f"Target {iso_date}"


def trello_id_created_at(card_id: str) -> datetime | None:
    """
    Decode the creation timestamp embedded in a Trello object id.

    The first 8 hex characters are seconds since the Unix epoch.
    """
    if not card_id or len(card_id) < 8:
        return None
    try:
        return datetime.fromtimestamp(int(card_id[:8], 16), tz=timezone.utc)
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def parse_trello_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        # Trello returns ISO-8601; fromisoformat handles most forms with Z replaced.
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return datetime.strptime(text[:10], "%Y-%m-%d").date()
        except ValueError:
            return None


def format_date_field(value: Any, *, field_name: str = "date") -> str | None:
    """Convert Excel/Python dates to ISO-8601 for Trello due/start fields."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if pd.isna(value):
        return None

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime().isoformat()

    text = str(value).strip()
    if not text:
        return None

    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        raise ValueError(f"Could not parse {field_name}: {value!r}")
    return parsed.to_pydatetime().isoformat()


def format_due(value: Any) -> str | None:
    """Convert Excel/Python dates to ISO-8601 for the Trello API `due` field."""
    return format_date_field(value, field_name="due date")


def format_pos(value: Any) -> str | float | None:
    """Normalize Position/Pos for the Trello API `pos` field."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if pd.isna(value):
        return None

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)

    text = str(value).strip()
    if not text:
        return None

    lowered = text.lower()
    if lowered in {"top", "bottom"}:
        return lowered

    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(
            f"Could not parse position: {value!r} (use top, bottom, or a number)"
        ) from exc
