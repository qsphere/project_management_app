from __future__ import annotations

from datetime import date
from typing import Any

from constants.entity_config import MAPS_TO_LABELS, MAPS_TO_LISTS
from functions.burndown import build_burndown_series, card_lifecycle
from functions.dashboard_breakdown import (
    lifecycle_breakdown,
    lifecycle_counts,
    list_breakdown,
)


def _risk_status(
    group: list[dict[str, Any]],
    burndown: list[dict[str, Any]],
    target: date | None,
    today: date,
) -> str:
    open_count = sum(1 for card in group if card["open"])
    remaining_today = open_count
    ideal_today = 0.0
    if burndown:
        today_point = next((p for p in burndown if p.get("is_today")), burndown[-1])
        ideal_today = float(today_point["ideal"])
        remaining_today = int(today_point["remaining"])
    behind = remaining_today > ideal_today + 0.5
    past_due = bool(target and target < today and open_count > 0)
    return "At Risk" if (behind or past_due) else "On Track"


def _initiative_row(
    *,
    entity_id: str,
    name: str,
    color: str | None,
    group: list[dict[str, Any]],
    today: date,
) -> dict[str, Any]:
    total = len(group)
    open_count = sum(1 for card in group if card["open"])
    pct = round(100.0 * (total - open_count) / total) if total else 0
    burndown, _, target = build_burndown_series(group, today=today)
    counts = lifecycle_counts(group)
    return {
        "id": entity_id,
        "name": name,
        "color": color,
        "total": total,
        "open": open_count,
        "complete_pct": pct,
        "status": _risk_status(group, burndown, target, today),
        "list_counts": counts,
        "status_breakdown": lifecycle_breakdown(counts),
        "target_date": target.isoformat() if target else None,
        "burndown": burndown,
    }


def build_initiative_dashboard(
    labels: list[dict[str, Any]],
    cards: list[dict[str, Any]],
    lists: list[dict[str, str]],
    *,
    today: date | None = None,
    initiative_maps_to: str = MAPS_TO_LABELS,
    lifecycle_filter: set[str] | None = None,
) -> dict[str, Any]:
    """
    Build the initiative dashboard from board data + initiative maps_to.

    Status pies always use derived lifecycleStatus (OPEN / CLOSED / ARCHIVED).
    Initiative grouping follows ``initiative_maps_to`` (Labels or Lists).
    """
    today = today or date.today()
    labels_ordered = [item for item in labels if (item.get("name") or "").strip()]
    label_index = {item["id"]: item for item in labels}

    enriched = [{**card, **card_lifecycle(card)} for card in cards]
    if lifecycle_filter is not None:
        enriched = [
            card
            for card in enriched
            if card["lifecycleStatus"] in lifecycle_filter
        ]

    overall_counts = lifecycle_counts(enriched)
    total_tasks = len(enriched)
    open_tasks = sum(1 for card in enriched if card["open"])
    complete_pct = (
        round(100.0 * (total_tasks - open_tasks) / total_tasks) if total_tasks else 0
    )
    overall_burndown, _, overall_target = build_burndown_series(enriched, today=today)

    initiatives: list[dict[str, Any]] = []
    if initiative_maps_to == MAPS_TO_LISTS:
        for item in lists:
            group = [c for c in enriched if c.get("idList") == item["id"]]
            if not group:
                continue
            initiatives.append(
                _initiative_row(
                    entity_id=item["id"],
                    name=item.get("name") or "(unnamed)",
                    color=None,
                    group=group,
                    today=today,
                )
            )
    else:
        for label in labels_ordered:
            label_id = label["id"]
            group = [
                c for c in enriched if label_id in (c.get("idLabels") or [])
            ]
            if not group:
                continue
            initiatives.append(
                _initiative_row(
                    entity_id=label_id,
                    name=label.get("name") or "(unnamed)",
                    color=label.get("color"),
                    group=group,
                    today=today,
                )
            )

    initiatives.sort(key=lambda item: (-item["total"], item["name"].lower()))
    entity_count = (
        len(lists) if initiative_maps_to == MAPS_TO_LISTS else len(labels_ordered)
    )

    return {
        "as_of": today.isoformat(),
        "total_tasks": total_tasks,
        "open_tasks": open_tasks,
        "complete_pct": complete_pct,
        "list_counts": overall_counts,
        "status_breakdown": lifecycle_breakdown(overall_counts),
        "overall_burndown": overall_burndown,
        "overall_target": overall_target.isoformat() if overall_target else None,
        "initiatives": initiatives,
        "label_count": entity_count,
        "unused_labels": entity_count - len(initiatives),
        "labels": label_index,
        "initiative_maps_to": initiative_maps_to,
    }


__all__ = ["build_initiative_dashboard", "list_breakdown"]
