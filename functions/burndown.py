from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from constants.status import LIFECYCLE_ARCHIVED, LIFECYCLE_CLOSED
from functions.dates import parse_trello_date, trello_id_created_at
from functions.status import compute_lifecycle_status


def is_complete_lifecycle(lifecycle_status: str) -> bool:
    return lifecycle_status in {LIFECYCLE_CLOSED, LIFECYCLE_ARCHIVED}


def card_lifecycle(card: dict[str, Any]) -> dict[str, Any]:
    """Derive lifecycleStatus, completion, and dates for one card (no list status)."""
    lifecycle_status = compute_lifecycle_status(card)
    complete = is_complete_lifecycle(lifecycle_status)
    created = trello_id_created_at(str(card.get("id") or ""))
    created_day = created.date() if created else None
    start_day = parse_trello_date(card.get("start")) or created_day
    due_day = parse_trello_date(card.get("due"))
    activity_day = parse_trello_date(card.get("dateLastActivity"))

    completed_day: date | None = None
    if complete:
        # Prefer due date when marked complete; otherwise last activity / today.
        completed_day = due_day if card.get("dueComplete") and due_day else None
        completed_day = completed_day or activity_day or due_day or date.today()

    return {
        "lifecycleStatus": lifecycle_status,
        "start_day": start_day,
        "due_day": due_day,
        "created_day": created_day,
        "completed_day": completed_day if complete else None,
        "complete": complete,
        "open": not complete,
    }


def build_burndown_series(
    cards: list[dict[str, Any]],
    *,
    today: date | None = None,
) -> tuple[list[dict[str, Any]], date | None, date | None]:
    """
    Build remaining-vs-ideal burndown points for a set of enriched card lifecycles.

    Each card dict must include start_day / completed_day / due_day / open
    (from ``card_lifecycle``). Ideal pace is a straight line from total at the
    series start down to 0 on the target date (latest due, else today).
    """
    today = today or date.today()
    if not cards:
        return [], None, None

    starts = [c["start_day"] for c in cards if c.get("start_day")]
    dues = [c["due_day"] for c in cards if c.get("due_day")]
    start_day = min(starts) if starts else today
    target_day = max(dues) if dues else today
    if target_day < start_day:
        target_day = start_day
    # Extend the chart at least through today so "now" is visible.
    end_day = max(target_day, today)

    total = len(cards)
    span_days = max((target_day - start_day).days, 1)
    # Daily points for short ranges; weekly for longer so charts stay light.
    step = 1 if (end_day - start_day).days <= 120 else 7
    points: list[dict[str, Any]] = []
    cursor = start_day
    while cursor <= end_day:
        completed = sum(
            1
            for card in cards
            if card.get("completed_day") and card["completed_day"] <= cursor
        )
        remaining = total - completed
        elapsed = (cursor - start_day).days
        ideal = max(total - (total * elapsed / span_days), 0.0)
        points.append(
            {
                "date": cursor.isoformat(),
                "remaining": remaining,
                "ideal": round(ideal, 2),
                "is_today": cursor == today,
            }
        )
        cursor += timedelta(days=step)

    # Always include today and the end date so the "now" marker and finish land.
    for forced in (today, end_day):
        if start_day <= forced <= end_day and not any(
            p["date"] == forced.isoformat() for p in points
        ):
            completed = sum(
                1
                for card in cards
                if card.get("completed_day") and card["completed_day"] <= forced
            )
            elapsed = (forced - start_day).days
            ideal = max(total - (total * elapsed / span_days), 0.0)
            points.append(
                {
                    "date": forced.isoformat(),
                    "remaining": total - completed,
                    "ideal": round(ideal, 2),
                    "is_today": forced == today,
                }
            )
    points.sort(key=lambda p: p["date"])

    return points, start_day, target_day
