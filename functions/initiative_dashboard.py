"""Build the initiative / taxonomy dashboard payload from board data."""

from __future__ import annotations

from datetime import date
from typing import Any

from constants.taxonomy import DIM_INITIATIVE, UNMAPPED_SHOW
from functions.burndown import build_burndown_series, card_lifecycle
from functions.dashboard_breakdown import (
    lifecycle_breakdown,
    lifecycle_counts,
    list_breakdown,
)
from functions.dashboard_rollups import (
    is_rollup_dimension,
    rollups_from_taxonomy,
)
from functions.taxonomy import dimension_source_map
from functions.taxonomy_filter import (
    annotate_card_taxonomy,
    dimension_keys_with_mappings,
    filter_annotated_cards,
)


def _board_lookups(
    labels: list[dict[str, Any]], lists: list[dict[str, str]]
) -> tuple[dict[str, str], dict[str, str]]:
    list_by_id = {item["id"]: item.get("name") or "" for item in lists}
    label_by_id = {
        item["id"]: item.get("name") or ""
        for item in labels
        if (item.get("name") or "").strip()
    }
    return list_by_id, label_by_id


def _enrich_cards(
    cards: list[dict[str, Any]],
    *,
    labels: list[dict[str, Any]],
    lists: list[dict[str, str]],
    mappings: list[dict[str, Any]],
    unmapped_policy: str,
    board_name: str | None,
) -> list[dict[str, Any]]:
    list_by_id, label_by_id = _board_lookups(labels, lists)
    dim_keys = dimension_keys_with_mappings(mappings)
    sources = dimension_source_map(mappings)
    enriched: list[dict[str, Any]] = []
    for card in cards:
        row = {**card, **card_lifecycle(card)}
        row["taxonomy"] = annotate_card_taxonomy(
            row,
            list_by_id=list_by_id,
            label_by_id=label_by_id,
            sources=sources,
            dimension_keys=dim_keys,
            unmapped_policy=unmapped_policy,
            board_name=board_name,
        )
        enriched.append(row)
    return enriched


def _visible_task_rows(
    cards: list[dict[str, Any]], group_dimension_key: str | None
) -> list[dict[str, Any]]:
    """Flatten visible cards for the dashboard task table (all dim values)."""
    rows: list[dict[str, Any]] = []
    for card in cards:
        taxonomy = card.get("taxonomy") or {}
        group_vals = (
            taxonomy.get(group_dimension_key) or []
            if group_dimension_key
            else []
        )
        rows.append(
            {
                "name": card.get("name") or "(unnamed)",
                "lifecycleStatus": card.get("lifecycleStatus"),
                "group_values": ", ".join(group_vals) if group_vals else "",
                "taxonomy": {
                    key: ", ".join(vals) if vals else ""
                    for key, vals in taxonomy.items()
                },
            }
        )
    return rows


def build_initiative_dashboard(
    labels: list[dict[str, Any]],
    cards: list[dict[str, Any]],
    lists: list[dict[str, str]],
    *,
    today: date | None = None,
    lifecycle_filter: set[str] | None = None,
    group_dimension_key: str | None = None,
    taxonomy_mappings: list[dict[str, Any]] | None = None,
    taxonomy_filters: dict[str, set[str]] | None = None,
    unmapped_policy: str = UNMAPPED_SHOW,
    board_name: str | None = None,
) -> dict[str, Any]:
    """
    Build the dashboard from board data.

    Lifecycle filter applies to overall charts and the visible task list (FR3.3).
    Feature/initiative rollups keep ARCHIVED in completion math (FR3.6–FR3.8).
    Grouping uses dimension → Trello field mappings (raw names as values).
    """
    today = today or date.today()
    label_index = {item["id"]: item for item in labels}

    mappings = list(taxonomy_mappings or [])
    enriched = _enrich_cards(
        cards,
        labels=labels,
        lists=lists,
        mappings=mappings,
        unmapped_policy=unmapped_policy,
        board_name=board_name,
    )
    scoped = filter_annotated_cards(
        enriched,
        taxonomy_filters=taxonomy_filters,
        lifecycle_filter=None,
    )
    visible = filter_annotated_cards(
        scoped,
        taxonomy_filters=None,
        lifecycle_filter=lifecycle_filter,
    )

    overall_counts = lifecycle_counts(visible)
    total_tasks = len(visible)
    open_tasks = sum(1 for card in visible if card["open"])
    complete_pct = (
        round(100.0 * (total_tasks - open_tasks) / total_tasks) if total_tasks else 0
    )
    overall_burndown, _, overall_target = build_burndown_series(visible, today=today)

    group_key = group_dimension_key
    dim_keys = dimension_keys_with_mappings(mappings)
    if group_key is None and DIM_INITIATIVE in dim_keys:
        group_key = DIM_INITIATIVE
    elif group_key is None and dim_keys:
        group_key = dim_keys[0]
    use_taxonomy = bool(group_key and group_key in dim_keys)
    rollup_cards = scoped if is_rollup_dimension(group_key) else visible

    initiatives: list[dict[str, Any]] = []
    entity_count = 0
    if use_taxonomy:
        initiatives, entity_count = rollups_from_taxonomy(
            cards=rollup_cards,
            labels=labels,
            lists=lists,
            dimension_key=group_key or DIM_INITIATIVE,
            mappings=mappings,
            unmapped_policy=unmapped_policy,
            today=today,
            board_name=board_name,
        )
        allowed = (taxonomy_filters or {}).get(group_key or "")
        if allowed:
            initiatives = [row for row in initiatives if row["name"] in allowed]

    initiatives.sort(key=lambda item: (-item["total"], item["name"].lower()))
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
        "unused_labels": max(0, entity_count - len(initiatives)),
        "labels": label_index,
        "uses_taxonomy": use_taxonomy,
        "group_dimension_key": group_key,
        "visible_tasks": _visible_task_rows(visible, group_key),
    }


__all__ = ["build_initiative_dashboard", "list_breakdown"]
