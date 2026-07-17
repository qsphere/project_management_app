from __future__ import annotations

from datetime import date
from typing import Any

from functions.dates import parse_trello_date


def card_choice_label(card: dict, list_id_to_name: dict[str, str]) -> str:
    list_name = list_id_to_name.get(card.get("idList") or "", "?")
    return f"{card['name'] or '(unnamed)'} · {list_name}"


def unique_card_choices(
    cards: list[dict], list_id_to_name: dict[str, str]
) -> dict[str, dict]:
    """Map display labels to cards, disambiguating duplicate name/list pairs."""
    counts: dict[str, int] = {}
    for card in cards:
        label = card_choice_label(card, list_id_to_name)
        counts[label] = counts.get(label, 0) + 1
    choices: dict[str, dict] = {}
    for card in cards:
        label = card_choice_label(card, list_id_to_name)
        if counts[label] > 1:
            label = f"{label} · {card['id'][:8]}"
        choices[label] = card
    return choices


def filter_cards(
    cards: list[dict[str, Any]],
    *,
    list_id: str | None = None,
    label_ids: list[str] | None = None,
    member_ids: list[str] | None = None,
    due_from: date | None = None,
    due_to: date | None = None,
    include_no_due: bool = True,
    unassigned_only: bool = False,
    no_labels_only: bool = False,
) -> list[dict[str, Any]]:
    """
    Filter cards by list, labels, assignees, and due-date range.

    Label/assignee filters match if the card has *any* of the selected IDs.
    Date bounds use the card's due date (calendar day). When a due range is set
    and include_no_due is False, cards without a due date are excluded.
    """
    label_set = set(label_ids or [])
    member_set = set(member_ids or [])
    date_filter_active = due_from is not None or due_to is not None

    filtered: list[dict[str, Any]] = []
    for card in cards:
        if list_id and card.get("idList") != list_id:
            continue

        card_labels = set(card.get("idLabels") or [])
        if no_labels_only:
            if card_labels:
                continue
        elif label_set and card_labels.isdisjoint(label_set):
            continue

        card_members = set(card.get("idMembers") or [])
        if unassigned_only:
            if card_members:
                continue
        elif member_set and card_members.isdisjoint(member_set):
            continue

        due_day = parse_trello_date(card.get("due"))
        if date_filter_active:
            if due_day is None:
                if not include_no_due:
                    continue
            else:
                if due_from is not None and due_day < due_from:
                    continue
                if due_to is not None and due_day > due_to:
                    continue
        elif not include_no_due and due_day is None:
            continue

        filtered.append(card)
    return filtered
