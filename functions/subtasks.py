"""Normalize Trello checklists/check items as subtasks; Excel encode/decode."""

from __future__ import annotations

from typing import Any

DEFAULT_CHECKLIST_NAME = "Subtasks"


def subtask_progress(card: dict[str, Any]) -> tuple[int, int]:
    """
    Return (done, total) subtask counts for a card.

    Prefers ``badges.checkItemsChecked`` / ``badges.checkItems``; falls back to
    nested ``checklists`` checkItems when badges are absent.
    """
    badges = card.get("badges") or {}
    if "checkItems" in badges:
        total = int(badges.get("checkItems") or 0)
        done = int(badges.get("checkItemsChecked") or 0)
        return done, total

    done = 0
    total = 0
    for group in checklists_to_subtask_groups(card.get("checklists") or []):
        for item in group["items"]:
            total += 1
            if item["complete"]:
                done += 1
    return done, total


def format_subtask_progress(card: dict[str, Any]) -> str:
    """Human-readable progress for the Cards table (``done/total`` or ``—``)."""
    done, total = subtask_progress(card)
    if total <= 0:
        return "—"
    return f"{done}/{total}"


def checklists_to_subtask_groups(
    checklists: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Normalize Trello checklists into subtask groups.

    Each group: ``{id, name, items: [{id, name, complete}]}``.
    """
    groups: list[dict[str, Any]] = []
    for checklist in checklists:
        items: list[dict[str, Any]] = []
        for raw in checklist.get("checkItems") or []:
            state = (raw.get("state") or "incomplete").strip().lower()
            items.append(
                {
                    "id": raw.get("id") or "",
                    "name": raw.get("name") or "",
                    "complete": state == "complete",
                }
            )
        groups.append(
            {
                "id": checklist.get("id") or "",
                "name": checklist.get("name") or DEFAULT_CHECKLIST_NAME,
                "items": items,
            }
        )
    return groups


def encode_subtasks_cell(checklists: list[dict[str, Any]]) -> str:
    """
    Serialize checklists/check items for the Excel Subtasks column.

    Format: ``Group: item1 | item2; Other: item3``. Bare default group name
    ``Subtasks`` is omitted when it is the only group.
    """
    groups = checklists_to_subtask_groups(checklists)
    if not groups:
        return ""

    parts: list[str] = []
    single_default = (
        len(groups) == 1 and groups[0]["name"] == DEFAULT_CHECKLIST_NAME
    )
    for group in groups:
        names = [str(item["name"]).strip() for item in group["items"]]
        names = [n for n in names if n]
        if not names:
            continue
        joined = " | ".join(names)
        if single_default:
            parts.append(joined)
        else:
            parts.append(f"{group['name']}: {joined}")
    return "; ".join(parts)


def parse_subtasks_cell(value: str | None) -> list[dict[str, Any]]:
    """
    Parse an Excel Subtasks cell into ``[{name, items: [str, ...]}, ...]``.

    - ``;`` separates groups
    - ``|`` separates items within a group
    - ``Group: items`` names the checklist; bare items use ``Subtasks``
    - Checked state is not encoded (import always creates incomplete items)
    """
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []

    groups: list[dict[str, Any]] = []
    for raw_group in text.split(";"):
        chunk = raw_group.strip()
        if not chunk:
            continue
        if ":" in chunk:
            name_part, items_part = chunk.split(":", 1)
            group_name = name_part.strip() or DEFAULT_CHECKLIST_NAME
            items_raw = items_part.strip()
        else:
            group_name = DEFAULT_CHECKLIST_NAME
            items_raw = chunk
        items = [part.strip() for part in items_raw.split("|") if part.strip()]
        if not items:
            continue
        # Merge into an existing group with the same name (case-sensitive).
        existing = next((g for g in groups if g["name"] == group_name), None)
        if existing is not None:
            existing["items"].extend(items)
        else:
            groups.append({"name": group_name, "items": items})
    return groups


__all__ = [
    "DEFAULT_CHECKLIST_NAME",
    "checklists_to_subtask_groups",
    "encode_subtasks_cell",
    "format_subtask_progress",
    "parse_subtasks_cell",
    "subtask_progress",
]
