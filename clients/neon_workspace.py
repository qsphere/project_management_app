"""Neon workspace + membership table helpers (mixin for NeonClient)."""

from __future__ import annotations

from typing import Any


class NeonWorkspaceMixin:
    """SQL for ``app_workspaces`` / ``app_workspace_members``."""

    def ensure_workspaces_tables(self) -> None:
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS app_workspaces (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                owner_user_id BIGINT NOT NULL
                    REFERENCES app_users(id) ON DELETE CASCADE,
                unmapped_policy TEXT NOT NULL DEFAULT 'show',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS app_workspace_members (
                id BIGSERIAL PRIMARY KEY,
                workspace_id BIGINT NOT NULL
                    REFERENCES app_workspaces(id) ON DELETE CASCADE,
                user_id BIGINT NOT NULL
                    REFERENCES app_users(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (workspace_id, user_id)
            )
            """
        )

    def get_owned_workspace(
        self, owner_user_id: int | str
    ) -> dict[str, Any] | None:
        return self.execute_one(
            """
            SELECT id, name, owner_user_id, unmapped_policy
            FROM app_workspaces
            WHERE owner_user_id = %s
            ORDER BY id ASC
            LIMIT 1
            """,
            (owner_user_id,),
        )

    def create_workspace(
        self, *, name: str, owner_user_id: int | str, unmapped_policy: str
    ) -> dict[str, Any]:
        row = self.execute_one(
            """
            INSERT INTO app_workspaces (name, owner_user_id, unmapped_policy)
            VALUES (%s, %s, %s)
            RETURNING id, name, owner_user_id, unmapped_policy
            """,
            (name, owner_user_id, unmapped_policy),
        )
        if row is None:
            raise RuntimeError("Failed to create workspace")
        return row

    def add_workspace_member(
        self, *, workspace_id: int | str, user_id: int | str
    ) -> None:
        self.execute(
            """
            INSERT INTO app_workspace_members (workspace_id, user_id)
            VALUES (%s, %s)
            ON CONFLICT (workspace_id, user_id) DO NOTHING
            """,
            (workspace_id, user_id),
        )

    def is_workspace_member(
        self, *, workspace_id: int | str, user_id: int | str
    ) -> bool:
        row = self.execute_one(
            """
            SELECT 1 AS ok
            FROM app_workspace_members
            WHERE workspace_id = %s AND user_id = %s
            """,
            (workspace_id, user_id),
        )
        return bool(row)

    def update_workspace_unmapped_policy(
        self, *, workspace_id: int | str, unmapped_policy: str
    ) -> dict[str, Any]:
        row = self.execute_one(
            """
            UPDATE app_workspaces
            SET unmapped_policy = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING id, name, owner_user_id, unmapped_policy
            """,
            (unmapped_policy, workspace_id),
        )
        if row is None:
            raise RuntimeError("Failed to update workspace policy")
        return row
