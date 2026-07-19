"""Per-user entity configuration orchestration (Neon; no Streamlit)."""

from __future__ import annotations

from typing import Any

from clients import NeonClient
from constants.entity_config import (
    DEFAULT_ENTITY_CONFIGS,
    ENTITY_KEYS,
    MAPS_TO_OPTIONS,
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
    client.ensure_entity_configurations_table()
    return client


def _normalize(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "entity_key": str(row.get("entity_key") or "").strip(),
        "name": str(row.get("name") or "").strip(),
        "description": str(row.get("description") or "").strip(),
        "maps_to": str(row.get("maps_to") or "").strip(),
    }


def _seed_missing(client: NeonClient, user_id: int | str) -> None:
    rows = client.list_entity_configurations(user_id)
    existing = {row["entity_key"] for row in rows}
    for default in DEFAULT_ENTITY_CONFIGS:
        if default["entity_key"] in existing:
            continue
        client.upsert_entity_configuration(
            user_id=user_id,
            entity_key=default["entity_key"],
            name=default["name"],
            description=default["description"],
            maps_to=default["maps_to"],
        )
    # Repair early-branch seed that inverted Lists/Labels vs domain defaults.
    by_key = {row["entity_key"]: row for row in rows}
    init = by_key.get("initiative")
    status = by_key.get("status")
    if (
        init
        and status
        and init.get("maps_to") == "Lists"
        and status.get("maps_to") == "Labels"
        and (init.get("name") or "").strip() == "Initiative"
        and (status.get("name") or "").strip() == "Status"
    ):
        for default in DEFAULT_ENTITY_CONFIGS:
            client.upsert_entity_configuration(
                user_id=user_id,
                entity_key=default["entity_key"],
                name=default["name"],
                description=default["description"],
                maps_to=default["maps_to"],
            )


def list_entity_configurations(user_id: int | str) -> list[dict[str, Any]]:
    client = _client()
    _seed_missing(client, user_id)
    by_key = {
        row["entity_key"]: _normalize(row)
        for row in client.list_entity_configurations(user_id)
    }
    return [by_key[key] for key in ENTITY_KEYS if key in by_key]


def update_entity_configuration(
    *,
    user_id: int | str,
    entity_key: str,
    name: str,
    description: str,
    maps_to: str,
) -> dict[str, Any]:
    entity_key = entity_key.strip()
    name = name.strip()
    description = description.strip()
    maps_to = maps_to.strip()
    if entity_key not in ENTITY_KEYS:
        raise AuthError("Unknown configuration entity.")
    if not name:
        raise AuthError("Configuration name is required.")
    if maps_to not in MAPS_TO_OPTIONS:
        raise AuthError("Maps to must be Lists or Labels.")
    return _normalize(
        _client().upsert_entity_configuration(
            user_id=user_id,
            entity_key=entity_key,
            name=name,
            description=description,
            maps_to=maps_to,
        )
    )


def dashboard_entity_maps(
    user_id: int | str | None = None,
) -> dict[str, dict[str, str]]:
    """
    Resolve Initiative/Status maps_to for the dashboard.

    Uses the signed-in user's saved configs when ``user_id`` is set and the DB
    is available; otherwise returns defaults. Initiative ``maps_to`` drives
    Dashboard grouping; Status chart slices always use lifecycleStatus.
    """
    defaults = {
        row["entity_key"]: {
            "name": row["name"],
            "maps_to": row["maps_to"],
        }
        for row in DEFAULT_ENTITY_CONFIGS
    }
    if user_id is None:
        return defaults
    try:
        configs = list_entity_configurations(user_id)
    except Exception:
        return defaults
    resolved = dict(defaults)
    for row in configs:
        key = row["entity_key"]
        if key not in resolved:
            continue
        maps_to = row["maps_to"]
        if maps_to not in MAPS_TO_OPTIONS:
            continue
        resolved[key] = {
            "name": row["name"] or defaults[key]["name"],
            "maps_to": maps_to,
        }
    return resolved


__all__ = [
    "dashboard_entity_maps",
    "list_entity_configurations",
    "update_entity_configuration",
]
