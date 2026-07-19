from __future__ import annotations

from typing import Any

from constants.status import (
    LIFECYCLE_ARCHIVED,
    LIFECYCLE_CLOSED,
    LIFECYCLE_OPEN,
)


def compute_lifecycle_status(card: dict[str, Any]) -> str:
    """
    Derive read-only lifecycleStatus from card flags (recomputed each sync).

    Precedence (first match wins):
    1. closed → ARCHIVED
    2. due set and dueComplete → CLOSED
    3. else → OPEN (including cards with no due date)
    """
    if card.get("closed"):
        return LIFECYCLE_ARCHIVED
    if card.get("due") and card.get("dueComplete"):
        return LIFECYCLE_CLOSED
    return LIFECYCLE_OPEN
