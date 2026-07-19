"""Filter and annotate cards by taxonomy dimension values."""

from __future__ import annotations

from typing import Any

from functions.taxonomy import (
    apply_unmapped_policy,
    resolve_field_values,
)


def dimension_keys_with_mappings(mappings: list[dict[str, Any]]) -> list[str]:
    """Unique dimension keys that have a field mapping, stable order."""
    seen: set[str] = set()
    keys: list[str] = []
    for row in mappings:
        key = str(row.get("dimension_key") or "").strip()
        if key and key not in seen:
            seen.add(key)
            keys.append(key)
    return keys


def board_values_for_source(
    source_type: str,
    *,
    lists: list[dict[str, Any]],
    labels: list[dict[str, Any]],
    card_names: list[str] | None = None,
    board_name: str | None = None,
) -> list[str]:
    """Sorted distinct raw names available on the board for a source type."""
    if source_type == "lists":
        values = {
            str(item.get("name") or "").strip()
            for item in lists
            if str(item.get("name") or "").strip()
        }
    elif source_type == "labels":
        values = {
            str(item.get("name") or "").strip()
            for item in labels
            if str(item.get("name") or "").strip()
        }
    elif source_type == "cards":
        values = {
            name.strip() for name in (card_names or []) if (name or "").strip()
        }
    elif source_type == "boards":
        text = (board_name or "").strip()
        values = {text} if text else set()
    else:
        values = set()
    return sorted(values, key=str.lower)


def annotate_card_taxonomy(
    card: dict[str, Any],
    *,
    list_by_id: dict[str, str],
    label_by_id: dict[str, str],
    sources: dict[str, str],
    dimension_keys: list[str],
    unmapped_policy: str,
    board_name: str | None = None,
) -> dict[str, list[str]]:
    """
    Resolve all taxonomy values per dimension for one card.

    Multiple labels on a labels-mapped dimension yield multiple values (FR3.4).
    """
    list_name = list_by_id.get(card.get("idList") or "", "")
    label_names = [
        label_by_id[lid]
        for lid in (card.get("idLabels") or [])
        if lid in label_by_id
    ]
    out: dict[str, list[str]] = {}
    for key in dimension_keys:
        source_type = sources.get(key)
        if not source_type:
            out[key] = []
            continue
        raw = resolve_field_values(
            source_type=source_type,
            list_name=list_name,
            label_names=label_names,
            card_name=card.get("name"),
            board_name=board_name,
        )
        resolved = apply_unmapped_policy(raw, policy=unmapped_policy)
        out[key] = list(resolved) if resolved is not None else []
    return out


def card_matches_taxonomy_filters(
    taxonomy: dict[str, list[str]],
    filters: dict[str, set[str]],
) -> bool:
    """AND across dimensions; within a dimension, any selected value matches."""
    for dim_key, allowed in filters.items():
        if not allowed:
            continue
        values = taxonomy.get(dim_key) or []
        if not any(value in allowed for value in values):
            return False
    return True


def filter_annotated_cards(
    cards: list[dict[str, Any]],
    *,
    taxonomy_filters: dict[str, set[str]] | None,
    lifecycle_filter: set[str] | None,
) -> list[dict[str, Any]]:
    """Apply taxonomy then lifecycle filters to annotated cards."""
    out = cards
    if taxonomy_filters:
        out = [
            card
            for card in out
            if card_matches_taxonomy_filters(
                card.get("taxonomy") or {}, taxonomy_filters
            )
        ]
    if lifecycle_filter is not None:
        out = [
            card
            for card in out
            if card.get("lifecycleStatus") in lifecycle_filter
        ]
    return out


__all__ = [
    "annotate_card_taxonomy",
    "board_values_for_source",
    "card_matches_taxonomy_filters",
    "dimension_keys_with_mappings",
    "filter_annotated_cards",
]
