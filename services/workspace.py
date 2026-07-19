"""Personal workspace orchestration (Neon; no Streamlit)."""

from __future__ import annotations

from typing import Any

from clients import NeonClient
from constants.taxonomy import (
    DEFAULT_DIMENSIONS,
    DEFAULT_MAPPINGS,
    SOURCE_TYPE_LABELS,
    UNMAPPED_POLICIES,
    UNMAPPED_SHOW,
)
from services.auth import AuthError
from services.neon import connected_neon_client


def _client() -> NeonClient:
    client = connected_neon_client()
    if client is None:
        raise AuthError(
            "Database is not configured. Set DATABASE_URL in "
            ".streamlit/secrets.toml to enable accounts."
        )
    client.ensure_users_table()
    client.ensure_workspaces_tables()
    client.ensure_taxonomy_tables()
    return client


def _normalize_workspace(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": str(row.get("name") or "").strip(),
        "owner_user_id": row["owner_user_id"],
        "unmapped_policy": str(row.get("unmapped_policy") or UNMAPPED_SHOW),
    }


def _seed_default_dimensions(client: NeonClient, workspace_id: int | str) -> None:
    existing = {
        row["dimension_key"] for row in client.list_taxonomy_dimensions(workspace_id)
    }
    for dim in DEFAULT_DIMENSIONS:
        key = str(dim["dimension_key"])
        if key in existing:
            continue
        client.upsert_taxonomy_dimension(
            workspace_id=workspace_id,
            dimension_key=key,
            name=str(dim["name"]),
            is_default=bool(dim["is_default"]),
        )


def _seed_default_mappings(client: NeonClient, workspace_id: int | str) -> None:
    mapped = {
        row["dimension_key"] for row in client.list_taxonomy_mappings(workspace_id)
    }
    defaults = {m["dimension_key"]: m["source_type"] for m in DEFAULT_MAPPINGS}
    for dim in client.list_taxonomy_dimensions(workspace_id):
        key = str(dim["dimension_key"])
        if key in mapped:
            continue
        client.upsert_taxonomy_mapping(
            workspace_id=workspace_id,
            dimension_key=key,
            source_type=defaults.get(key, SOURCE_TYPE_LABELS),
        )


def ensure_personal_workspace(user_id: int | str) -> dict[str, Any]:
    """Return the user's personal workspace, creating it and defaults if needed."""
    client = _client()
    row = client.get_owned_workspace(user_id)
    if row is None:
        row = client.create_workspace(
            name="Personal",
            owner_user_id=user_id,
            unmapped_policy=UNMAPPED_SHOW,
        )
        client.add_workspace_member(workspace_id=row["id"], user_id=user_id)
    else:
        client.add_workspace_member(workspace_id=row["id"], user_id=user_id)
    _seed_default_dimensions(client, row["id"])
    _seed_default_mappings(client, row["id"])
    return _normalize_workspace(row)


def require_workspace_member(
    *, workspace_id: int | str, user_id: int | str
) -> NeonClient:
    client = _client()
    if not client.is_workspace_member(workspace_id=workspace_id, user_id=user_id):
        raise AuthError("You are not a member of this workspace.")
    return client


def update_unmapped_policy(
    *, user_id: int | str, unmapped_policy: str
) -> dict[str, Any]:
    policy = unmapped_policy.strip()
    if policy not in UNMAPPED_POLICIES:
        raise AuthError("Unmapped policy must be 'show' or 'exclude'.")
    workspace = ensure_personal_workspace(user_id)
    client = require_workspace_member(
        workspace_id=workspace["id"], user_id=user_id
    )
    return _normalize_workspace(
        client.update_workspace_unmapped_policy(
            workspace_id=workspace["id"], unmapped_policy=policy
        )
    )


__all__ = [
    "ensure_personal_workspace",
    "require_workspace_member",
    "update_unmapped_policy",
]
