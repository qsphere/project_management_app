"""Taxonomy dimension/mapping CRUD (Neon; no Streamlit)."""

from __future__ import annotations

from typing import Any

from constants.taxonomy import SOURCE_TYPE_LABELS, SOURCE_TYPES
from functions.taxonomy import slugify_dimension_key
from services.auth import AuthError
from services.workspace import (
    ensure_personal_workspace,
    require_workspace_member,
)


def _norm_dim(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "workspace_id": row["workspace_id"],
        "dimension_key": str(row.get("dimension_key") or "").strip(),
        "name": str(row.get("name") or "").strip(),
        "is_default": bool(row.get("is_default")),
    }


def _norm_map(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "workspace_id": row["workspace_id"],
        "dimension_key": str(row.get("dimension_key") or "").strip(),
        "source_type": str(row.get("source_type") or "").strip().lower(),
    }


def list_dimensions(user_id: int | str) -> list[dict[str, Any]]:
    workspace = ensure_personal_workspace(user_id)
    client = require_workspace_member(
        workspace_id=workspace["id"], user_id=user_id
    )
    return [_norm_dim(r) for r in client.list_taxonomy_dimensions(workspace["id"])]


def create_dimension(*, user_id: int | str, name: str) -> dict[str, Any]:
    name = name.strip()
    if not name:
        raise AuthError("Dimension name is required.")
    key = slugify_dimension_key(name)
    workspace = ensure_personal_workspace(user_id)
    client = require_workspace_member(
        workspace_id=workspace["id"], user_id=user_id
    )
    existing = {
        r["dimension_key"] for r in client.list_taxonomy_dimensions(workspace["id"])
    }
    if key in existing:
        raise AuthError(f"Dimension '{key}' already exists.")
    dim = _norm_dim(
        client.upsert_taxonomy_dimension(
            workspace_id=workspace["id"],
            dimension_key=key,
            name=name,
            is_default=False,
        )
    )
    client.upsert_taxonomy_mapping(
        workspace_id=workspace["id"],
        dimension_key=key,
        source_type=SOURCE_TYPE_LABELS,
    )
    return dim


def rename_dimension(
    *, user_id: int | str, dimension_key: str, name: str
) -> dict[str, Any]:
    name = name.strip()
    if not name:
        raise AuthError("Dimension name is required.")
    workspace = ensure_personal_workspace(user_id)
    client = require_workspace_member(
        workspace_id=workspace["id"], user_id=user_id
    )
    row = client.update_taxonomy_dimension_name(
        workspace_id=workspace["id"],
        dimension_key=dimension_key.strip(),
        name=name,
    )
    if row is None:
        raise AuthError("Dimension not found.")
    return _norm_dim(row)


def delete_dimension(*, user_id: int | str, dimension_key: str) -> None:
    key = dimension_key.strip()
    workspace = ensure_personal_workspace(user_id)
    client = require_workspace_member(
        workspace_id=workspace["id"], user_id=user_id
    )
    dims = {
        r["dimension_key"]: r
        for r in client.list_taxonomy_dimensions(workspace["id"])
    }
    dim = dims.get(key)
    if dim is None:
        raise AuthError("Dimension not found.")
    if dim.get("is_default"):
        raise AuthError("Default dimensions cannot be deleted.")
    client.delete_taxonomy_mappings_for_dimension(
        workspace_id=workspace["id"], dimension_key=key
    )
    client.delete_taxonomy_dimension(workspace_id=workspace["id"], dimension_key=key)


def list_mappings(user_id: int | str) -> list[dict[str, Any]]:
    workspace = ensure_personal_workspace(user_id)
    client = require_workspace_member(
        workspace_id=workspace["id"], user_id=user_id
    )
    return [_norm_map(r) for r in client.list_taxonomy_mappings(workspace["id"])]


def set_dimension_source(
    *, user_id: int | str, dimension_key: str, source_type: str
) -> dict[str, Any]:
    """Set the Trello field a dimension pulls its values from (1:1)."""
    source_type = source_type.strip().lower()
    dimension_key = dimension_key.strip()
    if source_type not in SOURCE_TYPES:
        raise AuthError("Source must be cards, lists, labels, or boards.")
    workspace = ensure_personal_workspace(user_id)
    client = require_workspace_member(
        workspace_id=workspace["id"], user_id=user_id
    )
    dim_keys = {
        r["dimension_key"] for r in client.list_taxonomy_dimensions(workspace["id"])
    }
    if dimension_key not in dim_keys:
        raise AuthError("Unknown dimension.")
    return _norm_map(
        client.upsert_taxonomy_mapping(
            workspace_id=workspace["id"],
            dimension_key=dimension_key,
            source_type=source_type,
        )
    )


__all__ = [
    "create_dimension",
    "delete_dimension",
    "list_dimensions",
    "list_mappings",
    "rename_dimension",
    "set_dimension_source",
]
