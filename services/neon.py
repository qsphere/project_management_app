"""Orchestration wrappers around ``clients.NeonClient`` (no raw DB I/O)."""

from __future__ import annotations

from clients import NeonClient
from functions.env import env


def connected_neon_client(database_url: str | None = None) -> NeonClient | None:
    """Build a client from ``database_url`` or ``DATABASE_URL`` env; None if unset."""
    url = (database_url if database_url is not None else env("DATABASE_URL")).strip()
    if not url:
        return None
    return NeonClient(url)


def ping_neon(client: NeonClient) -> bool:
    return client.ping()


__all__ = ["connected_neon_client", "ping_neon"]
