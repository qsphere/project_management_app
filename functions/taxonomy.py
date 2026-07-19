"""Pure taxonomy helpers: resolve field values, validate import."""

from __future__ import annotations

import re
from typing import Any

from constants.taxonomy import (
    SOURCE_TYPE_BOARDS,
    SOURCE_TYPE_CARDS,
    SOURCE_TYPE_LABELS,
    SOURCE_TYPE_LISTS,
    SOURCE_TYPES,
    TAXONOMY_JSON_VERSION,
    UNMAPPED_EXCLUDE,
    UNMAPPED_LABEL,
    UNMAPPED_POLICIES,
    UNMAPPED_SHOW,
)


def normalize_name(name: str | None) -> str:
    return (name or "").strip().lower()


def slugify_dimension_key(name: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", (name or "").strip().lower())
    return key.strip("_") or "dimension"


def dimension_source_map(
    mappings: list[dict[str, Any]],
) -> dict[str, str]:
    """Map dimension_key → source_type."""
    out: dict[str, str] = {}
    for row in mappings:
        key = str(row.get("dimension_key") or "").strip()
        source = str(row.get("source_type") or "").strip().lower()
        if key and source in SOURCE_TYPES:
            out[key] = source
    return out


def resolve_field_values(
    *,
    source_type: str,
    list_name: str | None,
    label_names: list[str],
    card_name: str | None = None,
    board_name: str | None = None,
) -> list[str]:
    """Return raw Trello field names for a card given a source_type."""
    if source_type == SOURCE_TYPE_LISTS:
        text = (list_name or "").strip()
        return [text] if text else []
    if source_type == SOURCE_TYPE_LABELS:
        values: list[str] = []
        seen: set[str] = set()
        for name in label_names:
            text = (name or "").strip()
            if text and text not in seen:
                seen.add(text)
                values.append(text)
        return values
    if source_type == SOURCE_TYPE_CARDS:
        text = (card_name or "").strip()
        return [text] if text else []
    if source_type == SOURCE_TYPE_BOARDS:
        text = (board_name or "").strip()
        return [text] if text else []
    return []


def apply_unmapped_policy(
    values: list[str], *, policy: str
) -> list[str] | None:
    """
    Return values to group by, or None if the card should be excluded.

    Empty values + show → [Unmapped]; empty + exclude → None.
    """
    if values:
        return values
    if policy == UNMAPPED_EXCLUDE:
        return None
    return [UNMAPPED_LABEL]


def group_cards_by_dimension(
    *,
    cards: list[dict[str, Any]],
    dimension_key: str,
    list_by_id: dict[str, str],
    label_by_id: dict[str, str],
    mappings: list[dict[str, Any]],
    unmapped_policy: str,
    board_name: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Group cards by raw Trello field names for ``dimension_key``.

    Cards with no value follow ``unmapped_policy``. Multi-label cards appear
    in each matching label group.
    """
    sources = dimension_source_map(mappings)
    source_type = sources.get(dimension_key)
    if not source_type:
        return {}
    groups: dict[str, list[dict[str, Any]]] = {}
    for card in cards:
        list_name = list_by_id.get(card.get("idList") or "", "")
        label_names = [
            label_by_id[lid]
            for lid in (card.get("idLabels") or [])
            if lid in label_by_id
        ]
        values = resolve_field_values(
            source_type=source_type,
            list_name=list_name,
            label_names=label_names,
            card_name=card.get("name"),
            board_name=board_name,
        )
        resolved = apply_unmapped_policy(values, policy=unmapped_policy)
        if resolved is None:
            continue
        for value in resolved:
            groups.setdefault(value, []).append(card)
    return groups


def validate_import_payload(payload: Any) -> dict[str, Any]:
    """Validate and normalize a taxonomy JSON document. Raises ValueError."""
    if not isinstance(payload, dict):
        raise ValueError("Import JSON must be an object.")
    version = payload.get("version", TAXONOMY_JSON_VERSION)
    if version not in (1, TAXONOMY_JSON_VERSION):
        raise ValueError(f"Unsupported taxonomy JSON version: {version}")

    policy = str(payload.get("unmapped_policy") or UNMAPPED_SHOW).strip()
    if policy not in UNMAPPED_POLICIES:
        raise ValueError("unmapped_policy must be 'show' or 'exclude'.")

    raw_dims = payload.get("dimensions") or []
    if not isinstance(raw_dims, list):
        raise ValueError("dimensions must be a list.")
    dimensions: list[dict[str, str]] = []
    dim_keys: set[str] = set()
    for item in raw_dims:
        if not isinstance(item, dict):
            raise ValueError("Each dimension must be an object.")
        key = str(item.get("key") or item.get("dimension_key") or "").strip()
        name = str(item.get("name") or "").strip()
        if not key or not name:
            raise ValueError("Each dimension needs key and name.")
        if key in dim_keys:
            raise ValueError(f"Duplicate dimension key: {key}")
        dim_keys.add(key)
        dimensions.append({"dimension_key": key, "name": name})

    mappings = _parse_import_mappings(
        payload.get("mappings") or [], dim_keys=dim_keys, version=int(version)
    )
    return {
        "version": TAXONOMY_JSON_VERSION,
        "unmapped_policy": policy,
        "dimensions": dimensions,
        "mappings": mappings,
    }


def _parse_import_mappings(
    raw_maps: Any, *, dim_keys: set[str], version: int
) -> list[dict[str, str]]:
    if not isinstance(raw_maps, list):
        raise ValueError("mappings must be a list.")
    mappings: list[dict[str, str]] = []
    seen_dims: set[str] = set()
    for item in raw_maps:
        if not isinstance(item, dict):
            raise ValueError("Each mapping must be an object.")
        dimension_key = str(item.get("dimension_key") or "").strip()
        source_type = str(item.get("source_type") or "").strip().lower()
        if version == 1:
            # Legacy name→value rows: keep first source_type per dimension.
            if source_type in ("list", "lists"):
                source_type = SOURCE_TYPE_LISTS
            elif source_type in ("label", "labels"):
                source_type = SOURCE_TYPE_LABELS
            else:
                continue
        if source_type not in SOURCE_TYPES:
            raise ValueError(
                "source_type must be cards, lists, labels, or boards."
            )
        if not dimension_key:
            raise ValueError("Each mapping needs dimension_key.")
        if dim_keys and dimension_key not in dim_keys:
            raise ValueError(
                f"Mapping references unknown dimension_key: {dimension_key}"
            )
        if dimension_key in seen_dims:
            if version == 1:
                continue
            raise ValueError(
                f"Duplicate mapping for dimension '{dimension_key}'."
            )
        seen_dims.add(dimension_key)
        mappings.append(
            {"dimension_key": dimension_key, "source_type": source_type}
        )
    return mappings


__all__ = [
    "apply_unmapped_policy",
    "dimension_source_map",
    "group_cards_by_dimension",
    "normalize_name",
    "resolve_field_values",
    "slugify_dimension_key",
    "validate_import_payload",
]
