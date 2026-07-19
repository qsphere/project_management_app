"""Taxonomy JSON import/export and dashboard config load."""

from __future__ import annotations

import json
from typing import Any

from constants.taxonomy import (
    DEFAULT_DIMENSIONS,
    DEFAULT_MAPPINGS,
    TAXONOMY_JSON_VERSION,
    UNMAPPED_SHOW,
)
from functions.taxonomy import validate_import_payload
from services.taxonomy import list_dimensions, list_mappings
from services.workspace import (
    ensure_personal_workspace,
    require_workspace_member,
)


def export_taxonomy(user_id: int | str) -> dict[str, Any]:
    workspace = ensure_personal_workspace(user_id)
    dims = list_dimensions(user_id)
    maps = list_mappings(user_id)
    return {
        "version": TAXONOMY_JSON_VERSION,
        "unmapped_policy": workspace["unmapped_policy"],
        "dimensions": [
            {"key": d["dimension_key"], "name": d["name"]} for d in dims
        ],
        "mappings": [
            {
                "dimension_key": m["dimension_key"],
                "source_type": m["source_type"],
            }
            for m in maps
        ],
    }


def export_taxonomy_json(user_id: int | str) -> str:
    return json.dumps(export_taxonomy(user_id), indent=2)


def import_taxonomy(
    *,
    user_id: int | str,
    payload: Any,
    replace: bool = True,
) -> dict[str, Any]:
    """Import taxonomy JSON. ``replace=True`` clears existing mappings first."""
    data = validate_import_payload(payload)
    workspace = ensure_personal_workspace(user_id)
    client = require_workspace_member(
        workspace_id=workspace["id"], user_id=user_id
    )
    client.update_workspace_unmapped_policy(
        workspace_id=workspace["id"],
        unmapped_policy=data["unmapped_policy"],
    )
    default_keys = {str(d["dimension_key"]) for d in DEFAULT_DIMENSIONS}
    for dim in data["dimensions"]:
        client.upsert_taxonomy_dimension(
            workspace_id=workspace["id"],
            dimension_key=dim["dimension_key"],
            name=dim["name"],
            is_default=dim["dimension_key"] in default_keys,
        )
    if replace:
        client.delete_all_taxonomy_mappings(workspace["id"])
    for item in data["mappings"]:
        client.upsert_taxonomy_mapping(
            workspace_id=workspace["id"],
            dimension_key=item["dimension_key"],
            source_type=item["source_type"],
        )
    return export_taxonomy(user_id)


def default_taxonomy_config() -> dict[str, Any]:
    """In-memory defaults when the user is unsigned or DB is unavailable."""
    return {
        "workspace_id": None,
        "unmapped_policy": UNMAPPED_SHOW,
        "dimensions": [
            {
                "dimension_key": d["dimension_key"],
                "name": d["name"],
                "is_default": d["is_default"],
            }
            for d in DEFAULT_DIMENSIONS
        ],
        "mappings": [
            {
                "dimension_key": m["dimension_key"],
                "source_type": m["source_type"],
            }
            for m in DEFAULT_MAPPINGS
        ],
    }


def load_taxonomy_config(user_id: int | str | None) -> dict[str, Any]:
    """Load workspace taxonomy for dashboard use (always returns a config)."""
    if user_id is None:
        return default_taxonomy_config()
    try:
        workspace = ensure_personal_workspace(user_id)
        return {
            "workspace_id": workspace["id"],
            "unmapped_policy": workspace.get("unmapped_policy") or UNMAPPED_SHOW,
            "dimensions": list_dimensions(user_id),
            "mappings": list_mappings(user_id),
        }
    except Exception:
        return default_taxonomy_config()


__all__ = [
    "default_taxonomy_config",
    "export_taxonomy",
    "export_taxonomy_json",
    "import_taxonomy",
    "load_taxonomy_config",
]
