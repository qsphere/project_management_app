from __future__ import annotations

from datetime import date
from typing import Any

from constants.status import LIST_PALETTE
from functions.burndown import build_burndown_series, card_lifecycle


def list_breakdown(
    counts: dict[str, int],
    *,
    list_order: list[str],
) -> list[dict[str, Any]]:
    """
    Build pie-chart rows from list-name counts.

    Percentages are share of the group's cards (sums to ~100). Zero-count lists
    are omitted. Order follows board list order, then any extras.
    """
    total = sum(counts.values())
    ordered = [name for name in list_order if counts.get(name, 0) > 0]
    for name in counts:
        if name not in ordered and counts[name] > 0:
            ordered.append(name)

    rows: list[dict[str, Any]] = []
    for index, name in enumerate(ordered):
        count = counts[name]
        rows.append(
            {
                "status": name,  # chart/legend key (list name)
                "count": count,
                "pct": round(100.0 * count / total, 1) if total else 0.0,
                "color": LIST_PALETTE[index % len(LIST_PALETTE)],
            }
        )
    return rows


def build_initiative_dashboard(
    labels: list[dict[str, Any]],
    cards: list[dict[str, Any]],
    lists: list[dict[str, str]],
    *,
    today: date | None = None,
) -> dict[str, Any]:
    """
    Build an initiative dashboard where labels = initiatives and cards = tasks.

    Pie breakdowns use **board list names** (with percentages). Completion for
    burndown / % complete uses Done-like lists (e.g. Done, Fatto) and Archived.
    """
    today = today or date.today()
    list_names = {item["id"]: item["name"] for item in lists}
    list_order = [item["name"] for item in lists]

    enriched: list[dict[str, Any]] = []
    for card in cards:
        life = card_lifecycle(card, list_names)
        enriched.append({**card, **life})

    overall_list_counts: dict[str, int] = {}
    for card in enriched:
        name = card["list_name"]
        overall_list_counts[name] = overall_list_counts.get(name, 0) + 1

    total_tasks = len(enriched)
    open_tasks = sum(1 for card in enriched if card["open"])
    complete_pct = (
        round(100.0 * (total_tasks - open_tasks) / total_tasks) if total_tasks else 0
    )

    overall_burndown, _, overall_target = build_burndown_series(enriched, today=today)

    label_index = {item["id"]: item for item in labels}
    # Named labels with at least one card become initiative cards.
    named_labels = [item for item in labels if (item.get("name") or "").strip()]

    initiatives: list[dict[str, Any]] = []
    for label in named_labels:
        label_id = label["id"]
        group = [card for card in enriched if label_id in (card.get("idLabels") or [])]
        if not group:
            continue
        list_counts: dict[str, int] = {}
        for card in group:
            name = card["list_name"]
            list_counts[name] = list_counts.get(name, 0) + 1
        total = len(group)
        open_count = sum(1 for card in group if card["open"])
        done = sum(1 for card in group if not card["open"])
        pct = round(100.0 * done / total) if total else 0
        burndown, _, target = build_burndown_series(group, today=today)

        remaining_today = open_count
        ideal_today = 0.0
        if burndown:
            today_point = next(
                (p for p in burndown if p.get("is_today")), burndown[-1]
            )
            ideal_today = float(today_point["ideal"])
            remaining_today = int(today_point["remaining"])
        behind = remaining_today > ideal_today + 0.5
        blocked_n = sum(1 for card in group if card["status"] == "Blocked")
        blocked = blocked_n > 0 and (blocked_n / total >= 0.1 if total else False)
        past_due = bool(target and target < today and open_count > 0)
        status_label = "At Risk" if (behind or blocked or past_due) else "On Track"

        initiatives.append(
            {
                "id": label_id,
                "name": label.get("name") or "(unnamed)",
                "color": label.get("color"),
                "total": total,
                "open": open_count,
                "complete_pct": pct,
                "status": status_label,
                "list_counts": list_counts,
                "status_breakdown": list_breakdown(list_counts, list_order=list_order),
                "target_date": target.isoformat() if target else None,
                "burndown": burndown,
            }
        )

    # Stable order: most cards first, then name.
    initiatives.sort(key=lambda item: (-item["total"], item["name"].lower()))

    return {
        "as_of": today.isoformat(),
        "total_tasks": total_tasks,
        "open_tasks": open_tasks,
        "complete_pct": complete_pct,
        "list_counts": overall_list_counts,
        "status_breakdown": list_breakdown(overall_list_counts, list_order=list_order),
        "overall_burndown": overall_burndown,
        "overall_target": overall_target.isoformat() if overall_target else None,
        "initiatives": initiatives,
        "label_count": len(named_labels),
        "unused_labels": sum(
            1
            for label in named_labels
            if not any(
                label["id"] in (card.get("idLabels") or []) for card in enriched
            )
        ),
        "labels": label_index,
    }
