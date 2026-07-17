from __future__ import annotations

from typing import Any


def build_label_dashboard(
    labels: list[dict[str, Any]],
    cards: list[dict[str, Any]],
    lists: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """
    Aggregate open-card counts per label, broken down by list.

    Returns one dict per label:
      {
        id, name, color,
        total,  # cards with this label
        lists: [{list_id, list_name, count, pct_of_label, pct_of_list}, ...],
      }

    pct_of_label: share of this label's cards that sit in the list (sums to ~100).
    pct_of_list: share of that list's open cards that have this label.
    Lists with zero matching cards are omitted. Order follows board list order.
    """
    list_order = [item["id"] for item in lists]
    list_names = {item["id"]: item["name"] for item in lists}

    # Cards per list (for pct_of_list denominator).
    cards_per_list: dict[str, int] = {}
    for card in cards:
        list_id = card.get("idList") or ""
        if list_id:
            cards_per_list[list_id] = cards_per_list.get(list_id, 0) + 1

    # label_id → list_id → count
    counts: dict[str, dict[str, int]] = {item["id"]: {} for item in labels}
    totals: dict[str, int] = {item["id"]: 0 for item in labels}

    for card in cards:
        list_id = card.get("idList") or ""
        for label_id in card.get("idLabels") or []:
            if label_id not in counts:
                continue
            totals[label_id] += 1
            if list_id:
                counts[label_id][list_id] = counts[label_id].get(list_id, 0) + 1

    dashboard: list[dict[str, Any]] = []
    for label in labels:
        label_id = label["id"]
        total = totals[label_id]
        by_list: list[dict[str, Any]] = []
        for list_id in list_order:
            count = counts[label_id].get(list_id, 0)
            if count == 0:
                continue
            list_total = cards_per_list.get(list_id, 0)
            by_list.append(
                {
                    "list_id": list_id,
                    "list_name": list_names.get(list_id, list_id),
                    "count": count,
                    "pct_of_label": round(100.0 * count / total, 1) if total else 0.0,
                    "pct_of_list": (
                        round(100.0 * count / list_total, 1) if list_total else 0.0
                    ),
                }
            )
        # Include any list ids not in open_lists (e.g. archived list edge cases).
        for list_id, count in counts[label_id].items():
            if list_id in list_names:
                continue
            list_total = cards_per_list.get(list_id, 0)
            by_list.append(
                {
                    "list_id": list_id,
                    "list_name": list_id,
                    "count": count,
                    "pct_of_label": round(100.0 * count / total, 1) if total else 0.0,
                    "pct_of_list": (
                        round(100.0 * count / list_total, 1) if list_total else 0.0
                    ),
                }
            )
        dashboard.append(
            {
                "id": label_id,
                "name": label.get("name") or "",
                "color": label.get("color"),
                "total": total,
                "lists": by_list,
            }
        )
    return dashboard
