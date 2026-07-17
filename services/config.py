"""Trello connection orchestration (Neon + env defaults; no Streamlit)."""

from __future__ import annotations

from typing import Any

from clients import NeonClient
from functions.env import env
from services.auth import AuthError
from services.neon import connected_neon_client

CREDENTIAL_KEYS = ("api_key", "token", "board_id", "list_id")


def env_trello_config() -> dict[str, str]:
    return {
        "api_key": env("TRELLO_API_KEY"),
        "token": env("TRELLO_TOKEN"),
        "board_id": env("TRELLO_BOARD_ID"),
        "list_id": env("TRELLO_LIST_ID"),
    }


def _client() -> NeonClient:
    client = connected_neon_client()
    if client is None:
        raise AuthError(
            "Database is not configured. Set DATABASE_URL in .env to enable accounts."
        )
    client.ensure_users_table()
    client.ensure_trello_connections_table()
    return client


def _normalize(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": str(row.get("name") or "").strip(),
        "api_key": str(row.get("api_key") or "").strip(),
        "token": str(row.get("token") or "").strip(),
        "board_id": str(row.get("board_id") or "").strip(),
        "list_id": str(row.get("list_id") or "").strip(),
    }


def list_trello_connections(user_id: int | str) -> list[dict[str, Any]]:
    return [_normalize(row) for row in _client().list_trello_connections(user_id)]


def get_trello_connection(
    user_id: int | str, connection_id: int | str
) -> dict[str, Any] | None:
    row = _client().get_trello_connection(user_id, connection_id)
    return _normalize(row) if row else None


def create_trello_connection(
    *,
    user_id: int | str,
    name: str,
    api_key: str,
    token: str,
    board_id: str,
    list_id: str,
) -> dict[str, Any]:
    name = name.strip()
    if not name:
        raise AuthError("Connection name is required.")
    if not api_key.strip() or not token.strip() or not board_id.strip():
        raise AuthError("API key, token, and board ID are required.")
    return _normalize(
        _client().create_trello_connection(
            user_id=user_id,
            name=name,
            api_key=api_key.strip(),
            token=token.strip(),
            board_id=board_id.strip(),
            list_id=list_id.strip(),
        )
    )


def update_trello_connection(
    *,
    user_id: int | str,
    connection_id: int | str,
    name: str,
    api_key: str,
    token: str,
    board_id: str,
    list_id: str,
) -> dict[str, Any]:
    name = name.strip()
    if not name:
        raise AuthError("Connection name is required.")
    if not api_key.strip() or not token.strip() or not board_id.strip():
        raise AuthError("API key, token, and board ID are required.")
    row = _client().update_trello_connection(
        user_id=user_id,
        connection_id=connection_id,
        name=name,
        api_key=api_key.strip(),
        token=token.strip(),
        board_id=board_id.strip(),
        list_id=list_id.strip(),
    )
    if row is None:
        raise AuthError("Connection not found.")
    return _normalize(row)


def delete_trello_connection(
    *, user_id: int | str, connection_id: int | str
) -> None:
    if _client().delete_trello_connection(user_id, connection_id) is None:
        raise AuthError("Connection not found.")


def credentials_from_connection(conn: dict[str, Any] | None) -> dict[str, str]:
    if not conn:
        return {key: "" for key in CREDENTIAL_KEYS}
    return {key: str(conn.get(key) or "") for key in CREDENTIAL_KEYS}


__all__ = [
    "CREDENTIAL_KEYS",
    "create_trello_connection",
    "credentials_from_connection",
    "delete_trello_connection",
    "env_trello_config",
    "get_trello_connection",
    "list_trello_connections",
    "update_trello_connection",
]
