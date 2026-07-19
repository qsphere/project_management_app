"""Pie-chart breakdown helpers for the initiative dashboard."""

from __future__ import annotations

from typing import Any

from constants.status import LIFECYCLE_COLORS, LIFECYCLE_ORDER, LIST_PALETTE


def breakdown_from_counts(
    counts: dict[str, int],
    *,
    order: list[str],
    colors: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    total = sum(counts.values())
    ordered = [name for name in order if counts.get(name, 0) > 0]
    for name in counts:
        if name not in ordered and counts[name] > 0:
            ordered.append(name)

    rows: list[dict[str, Any]] = []
    for index, name in enumerate(ordered):
        count = counts[name]
        color = (
            colors.get(name, LIST_PALETTE[index % len(LIST_PALETTE)])
            if colors
            else LIST_PALETTE[index % len(LIST_PALETTE)]
        )
        rows.append(
            {
                "status": name,
                "count": count,
                "pct": round(100.0 * count / total, 1) if total else 0.0,
                "color": color,
            }
        )
    return rows


def list_breakdown(
    counts: dict[str, int],
    *,
    list_order: list[str],
) -> list[dict[str, Any]]:
    """Build pie-chart rows from name→count (zeros omitted; order then extras)."""
    return breakdown_from_counts(counts, order=list_order)


def lifecycle_counts(cards: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for card in cards:
        key = card["lifecycleStatus"]
        counts[key] = counts.get(key, 0) + 1
    return counts


def lifecycle_breakdown(counts: dict[str, int]) -> list[dict[str, Any]]:
    """Pie rows for lifecycle status buckets (OPEN / CLOSED / ARCHIVED)."""
    return breakdown_from_counts(
        counts,
        order=list(LIFECYCLE_ORDER),
        colors=LIFECYCLE_COLORS,
    )
