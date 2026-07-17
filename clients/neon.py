"""Neon Postgres client — sole place for database connections.

Uses psycopg (v3) against ``DATABASE_URL``. Prefer the pooled Neon URL
(hostname contains ``-pooler``) for the Streamlit app. Never log the URL.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Sequence

import psycopg
from psycopg.rows import dict_row


class NeonClient:
    """Thin Postgres wrapper. All SQL goes through this client."""

    def __init__(self, database_url: str):
        if not (database_url or "").strip():
            raise ValueError("DATABASE_URL is required")
        self._database_url = database_url.strip()

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection[dict[str, Any]]]:
        with psycopg.connect(self._database_url, row_factory=dict_row) as conn:
            yield conn

    def execute(
        self,
        query: str,
        params: Sequence[Any] | dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Run a query; return rows as dicts (empty list for non-SELECT)."""
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if cur.description is None:
                    conn.commit()
                    return []
                rows = list(cur.fetchall())
                conn.commit()
                return rows

    def execute_one(
        self,
        query: str,
        params: Sequence[Any] | dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        rows = self.execute(query, params)
        return rows[0] if rows else None

    def ping(self) -> bool:
        """Return True when the database answers ``SELECT 1``."""
        row = self.execute_one("SELECT 1 AS ok")
        return bool(row and row.get("ok") == 1)

    def ensure_users_table(self) -> None:
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS app_users (
                id BIGSERIAL PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )

    def create_user(
        self, *, full_name: str, email: str, password_hash: str
    ) -> dict[str, Any]:
        row = self.execute_one(
            """
            INSERT INTO app_users (full_name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, full_name, email
            """,
            (full_name, email, password_hash),
        )
        if row is None:
            raise RuntimeError("Failed to create user")
        return row

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        return self.execute_one(
            """
            SELECT id, full_name, email, password_hash
            FROM app_users
            WHERE email = %s
            """,
            (email,),
        )


__all__ = ["NeonClient"]
