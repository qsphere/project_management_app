"""Build dashboard rollup rows for taxonomy field grouping."""

from __future__ import annotations

from datetime import date
from typing import Any

from constants.taxonomy import DIM_INITIATIVE, ROLLUP_DIMENSIONS
from functions.burndown import build_burndown_series
from functions.dashboard_breakdown import lifecycle_breakdown, lifecycle_counts
from functions.taxonomy import group_cards_by_dimension


def risk_status(
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


def rollup_row(
    *,
    entity_id: str,
    name: str,
    color: str | None,
    group: list[dict[str, Any]],
    today: date,
) -> dict[str, Any]:
    """
    Completion = (CLOSED + ARCHIVED) / total mapped cards (FR3.6).

    ARCHIVED stays in numerator and denominator for feature/initiative (FR3.7).
    """
    total = len(group)
    open_count = sum(1 for card in group if card["open"])
    complete_n = total - open_count
    pct = round(100.0 * complete_n / total) if total else 0
    burndown, _, target = build_burndown_series(group, today=today)
    counts = lifecycle_counts(group)
    return {
        "id": entity_id,
        "name": name,
        "color": color,
        "total": total,
        "open": open_count,
        "complete_pct": pct,
        "status": risk_status(group, burndown, target, today),
        "list_counts": counts,
        "status_breakdown": lifecycle_breakdown(counts),
        "target_date": target.isoformat() if target else None,
        "burndown": burndown,
    }


def rollups_from_taxonomy(
    *,
    cards: list[dict[str, Any]],
    labels: list[dict[str, Any]],
    lists: list[dict[str, str]],
    dimension_key: str,
    mappings: list[dict[str, Any]],
    unmapped_policy: str,
    today: date,
    board_name: str | None = None,
) -> tuple[list[dict[str, Any]], int]:
    list_by_id = {item["id"]: item.get("name") or "" for item in lists}
    label_by_id = {
        item["id"]: item.get("name") or ""
        for item in labels
        if (item.get("name") or "").strip()
    }
    name_to_color = {
        (item.get("name") or ""): item.get("color")
        for item in labels
        if (item.get("name") or "").strip()
    }
    groups = group_cards_by_dimension(
        cards=cards,
        dimension_key=dimension_key,
        list_by_id=list_by_id,
        label_by_id=label_by_id,
        mappings=mappings,
        unmapped_policy=unmapped_policy,
        board_name=board_name,
    )
    rows = [
        rollup_row(
            entity_id=f"tax:{dimension_key}:{name}",
            name=name,
            color=name_to_color.get(name),
            group=group,
            today=today,
        )
        for name, group in groups.items()
        if group
    ]
    return rows, len(groups)


def is_rollup_dimension(dimension_key: str | None) -> bool:
    """Feature/initiative keep ARCHIVED in completion math."""
    if dimension_key is None:
        return True
    return dimension_key in ROLLUP_DIMENSIONS or dimension_key == DIM_INITIATIVE


__all__ = [
    "is_rollup_dimension",
    "rollups_from_taxonomy",
    "rollup_row",
    "risk_status",
]
