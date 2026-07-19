"""Neon entity-configuration table helpers (mixin for NeonClient)."""

from __future__ import annotations

from typing import Any


class NeonEntityConfigMixin:
    """SQL for ``app_entity_configurations``. Requires ``execute`` / ``execute_one``."""

    def ensure_entity_configurations_table(self) -> None:
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS app_entity_configurations (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL
                    REFERENCES app_users(id) ON DELETE CASCADE,
                entity_key TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                maps_to TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (user_id, entity_key)
            )
            """
        )

    def list_entity_configurations(
        self, user_id: int | str
    ) -> list[dict[str, Any]]:
        return self.execute(
            """
            SELECT id, entity_key, name, description, maps_to
            FROM app_entity_configurations
            WHERE user_id = %s
            ORDER BY entity_key ASC
            """,
            (user_id,),
        )

    def upsert_entity_configuration(
        self,
        *,
        user_id: int | str,
        entity_key: str,
        name: str,
        description: str,
        maps_to: str,
    ) -> dict[str, Any]:
        row = self.execute_one(
            """
            INSERT INTO app_entity_configurations
                (user_id, entity_key, name, description, maps_to)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, entity_key) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                maps_to = EXCLUDED.maps_to,
                updated_at = NOW()
            RETURNING id, entity_key, name, description, maps_to
            """,
            (user_id, entity_key, name, description, maps_to),
        )
        if row is None:
            raise RuntimeError("Failed to save entity configuration")
        return row
