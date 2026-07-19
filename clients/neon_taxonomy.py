"""Neon taxonomy dimension + mapping table helpers (mixin for NeonClient)."""

from __future__ import annotations

from typing import Any


class NeonTaxonomyMixin:
    """SQL for ``app_taxonomy_dimensions`` / ``app_taxonomy_mappings``."""

    def ensure_taxonomy_tables(self) -> None:
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS app_taxonomy_dimensions (
                id BIGSERIAL PRIMARY KEY,
                workspace_id BIGINT NOT NULL
                    REFERENCES app_workspaces(id) ON DELETE CASCADE,
                dimension_key TEXT NOT NULL,
                name TEXT NOT NULL,
                is_default BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (workspace_id, dimension_key)
            )
            """
        )
        self._ensure_field_mappings_table()

    def _ensure_field_mappings_table(self) -> None:
        """Create or migrate to dimension_key → source_type mappings."""
        legacy = self.execute_one(
            """
            SELECT 1 AS ok
            FROM information_schema.columns
            WHERE table_name = 'app_taxonomy_mappings'
              AND column_name = 'source_name'
            LIMIT 1
            """
        )
        if legacy:
            self.execute("DROP TABLE IF EXISTS app_taxonomy_mappings")
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS app_taxonomy_mappings (
                id BIGSERIAL PRIMARY KEY,
                workspace_id BIGINT NOT NULL
                    REFERENCES app_workspaces(id) ON DELETE CASCADE,
                dimension_key TEXT NOT NULL,
                source_type TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (workspace_id, dimension_key)
            )
            """
        )

    def list_taxonomy_dimensions(
        self, workspace_id: int | str
    ) -> list[dict[str, Any]]:
        return self.execute(
            """
            SELECT id, workspace_id, dimension_key, name, is_default
            FROM app_taxonomy_dimensions
            WHERE workspace_id = %s
            ORDER BY is_default DESC, name ASC
            """,
            (workspace_id,),
        )

    def upsert_taxonomy_dimension(
        self,
        *,
        workspace_id: int | str,
        dimension_key: str,
        name: str,
        is_default: bool,
    ) -> dict[str, Any]:
        row = self.execute_one(
            """
            INSERT INTO app_taxonomy_dimensions
                (workspace_id, dimension_key, name, is_default)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (workspace_id, dimension_key) DO UPDATE SET
                name = EXCLUDED.name,
                updated_at = NOW()
            RETURNING id, workspace_id, dimension_key, name, is_default
            """,
            (workspace_id, dimension_key, name, is_default),
        )
        if row is None:
            raise RuntimeError("Failed to save taxonomy dimension")
        return row

    def update_taxonomy_dimension_name(
        self,
        *,
        workspace_id: int | str,
        dimension_key: str,
        name: str,
    ) -> dict[str, Any] | None:
        return self.execute_one(
            """
            UPDATE app_taxonomy_dimensions
            SET name = %s, updated_at = NOW()
            WHERE workspace_id = %s AND dimension_key = %s
            RETURNING id, workspace_id, dimension_key, name, is_default
            """,
            (name, workspace_id, dimension_key),
        )

    def delete_taxonomy_dimension(
        self, *, workspace_id: int | str, dimension_key: str
    ) -> dict[str, Any] | None:
        return self.execute_one(
            """
            DELETE FROM app_taxonomy_dimensions
            WHERE workspace_id = %s AND dimension_key = %s
            RETURNING id, workspace_id, dimension_key, name, is_default
            """,
            (workspace_id, dimension_key),
        )

    def list_taxonomy_mappings(
        self, workspace_id: int | str
    ) -> list[dict[str, Any]]:
        return self.execute(
            """
            SELECT id, workspace_id, dimension_key, source_type
            FROM app_taxonomy_mappings
            WHERE workspace_id = %s
            ORDER BY dimension_key ASC
            """,
            (workspace_id,),
        )

    def upsert_taxonomy_mapping(
        self,
        *,
        workspace_id: int | str,
        dimension_key: str,
        source_type: str,
    ) -> dict[str, Any]:
        row = self.execute_one(
            """
            INSERT INTO app_taxonomy_mappings
                (workspace_id, dimension_key, source_type)
            VALUES (%s, %s, %s)
            ON CONFLICT (workspace_id, dimension_key) DO UPDATE SET
                source_type = EXCLUDED.source_type,
                updated_at = NOW()
            RETURNING id, workspace_id, dimension_key, source_type
            """,
            (workspace_id, dimension_key, source_type),
        )
        if row is None:
            raise RuntimeError("Failed to save taxonomy mapping")
        return row

    def delete_taxonomy_mappings_for_dimension(
        self, *, workspace_id: int | str, dimension_key: str
    ) -> None:
        self.execute(
            """
            DELETE FROM app_taxonomy_mappings
            WHERE workspace_id = %s AND dimension_key = %s
            """,
            (workspace_id, dimension_key),
        )

    def delete_all_taxonomy_mappings(self, workspace_id: int | str) -> None:
        self.execute(
            """
            DELETE FROM app_taxonomy_mappings WHERE workspace_id = %s
            """,
            (workspace_id,),
        )
