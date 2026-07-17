"""Label CRUD and name→id resolution (Trello HTTP)."""

from __future__ import annotations

from typing import Any

import pandas as pd

from constants.colors import LABEL_COLORS


class TrelloLabelsMixin:
    def board_labels(self) -> list[dict[str, Any]]:
        """
        Return all labels on the board as [{id, name, color, uses}, ...].

        Name may be empty for unnamed color-only labels. Color may be None.
        """
        labels = self._get(f"/boards/{self.board_id}/labels", limit=1000)
        return [
            {
                "id": item["id"],
                "name": item.get("name") or "",
                "color": item.get("color"),
                "uses": item.get("uses", 0),
            }
            for item in labels
        ]

    def labels_by_name(self) -> dict[str, str]:
        if self._labels_by_name is None:
            self._labels_by_name = {
                item["name"].strip().lower(): item["id"]
                for item in self.board_labels()
                if item.get("name")
            }
        return self._labels_by_name

    def _invalidate_labels_cache(self) -> None:
        self._labels_by_name = None

    def create_label(self, name: str, color: str | None) -> dict[str, Any]:
        """Create a label on this board via POST /labels."""
        params: dict[str, Any] = {
            "name": name,
            "idBoard": self.board_id,
        }
        if color:
            params["color"] = color
        else:
            params["color"] = "null"
        result = self._post("/labels", **params)
        self._invalidate_labels_cache()
        return result

    def update_label(
        self,
        label_id: str,
        *,
        name: str | None = None,
        color: str | None = None,
    ) -> dict[str, Any]:
        """Update a label via PUT /labels/{id}. Pass color='' to clear color."""
        params: dict[str, Any] = {}
        if name is not None:
            params["name"] = name
        if color is not None:
            params["color"] = color if color else "null"
        if not params:
            raise ValueError("Provide name and/or color to update.")
        result = self._put(f"/labels/{label_id}", **params)
        self._invalidate_labels_cache()
        return result

    def delete_label(self, label_id: str) -> None:
        """Delete a label via DELETE /labels/{id}."""
        self._delete(f"/labels/{label_id}")
        self._invalidate_labels_cache()

    def _next_label_color(self) -> str:
        """Pick a Trello label color not already used on this board."""
        used = {
            item.get("color")
            for item in self.board_labels()
            if item.get("color")
        }
        for color in LABEL_COLORS:
            if color not in used:
                return color
        # Every palette color is taken; cycle so new labels still get a color.
        return LABEL_COLORS[len(self.board_labels()) % len(LABEL_COLORS)]

    def resolve_label_ids(
        self,
        labels_value: str | None,
        *,
        create_missing: bool = True,
    ) -> tuple[list[str], list[str]]:
        """
        Resolve comma-separated label names to board label IDs.

        When create_missing is True, names that are not on the board are created
        with an unused color and their new IDs are returned.

        Returns (label_ids, created_names). When create_missing is False,
        created_names lists names that would be created (no API writes).
        """
        if not labels_value or pd.isna(labels_value):
            return [], []

        label_ids: list[str] = []
        created_names: list[str] = []
        # Local map so duplicate names in one cell (or before cache refresh) reuse
        # the same id / dry-run placeholder.
        resolved: dict[str, str] = {}

        for raw in str(labels_value).split(","):
            name = raw.strip()
            if not name:
                continue
            key = name.lower()

            if key in resolved:
                label_ids.append(resolved[key])
                continue

            label_id = self.labels_by_name().get(key)
            if label_id:
                resolved[key] = label_id
                label_ids.append(label_id)
                continue

            if not create_missing:
                placeholder = f"(new:{name})"
                resolved[key] = placeholder
                created_names.append(name)
                label_ids.append(placeholder)
                continue

            color = self._next_label_color()
            created = self.create_label(name, color)
            new_id = created["id"]
            # create_label clears the name→id cache; refresh and keep this entry.
            self.labels_by_name()[key] = new_id
            resolved[key] = new_id
            label_ids.append(new_id)
            created_names.append(name)

        return label_ids, created_names
