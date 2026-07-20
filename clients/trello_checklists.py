"""Checklist / check-item CRUD (Trello HTTP). Check items are app subtasks."""

from __future__ import annotations

from typing import Any


class TrelloChecklistsMixin:
    def card_checklists(self, card_id: str) -> list[dict[str, Any]]:
        """
        Return checklists (with checkItems) on a card.

        See: https://developer.atlassian.com/cloud/trello/rest/api-group-cards/#api-cards-id-checklists-get
        """
        return self._get(
            f"/cards/{card_id}/checklists",
            checkItems="all",
            checkItem_fields="name,state,pos",
            fields="name,pos",
        )

    def create_checklist(
        self, card_id: str, *, name: str = "Checklist"
    ) -> dict[str, Any]:
        """Create a checklist on a card via POST /cards/{id}/checklists."""
        return self._post(f"/cards/{card_id}/checklists", name=name)

    def delete_checklist(self, checklist_id: str) -> None:
        """Delete a checklist via DELETE /checklists/{id}."""
        self._delete(f"/checklists/{checklist_id}")

    def create_check_item(
        self,
        checklist_id: str,
        name: str,
        *,
        checked: bool = False,
        pos: str | float | None = None,
    ) -> dict[str, Any]:
        """
        Create a check item (subtask) via POST /checklists/{id}/checkItems.

        See: https://developer.atlassian.com/cloud/trello/rest/api-group-checklists/#api-checklists-id-checkitems-post
        """
        params: dict[str, Any] = {"name": name, "checked": checked}
        if pos is not None and pos != "":
            params["pos"] = pos
        return self._post(f"/checklists/{checklist_id}/checkItems", **params)

    def update_check_item(
        self,
        card_id: str,
        check_item_id: str,
        *,
        name: str | None = None,
        state: str | None = None,
    ) -> dict[str, Any]:
        """
        Update a check item via PUT /cards/{id}/checkItem/{idCheckItem}.

        ``state`` is ``complete`` or ``incomplete``.
        """
        params: dict[str, Any] = {}
        if name is not None:
            params["name"] = name
        if state is not None:
            params["state"] = state
        if not params:
            raise ValueError("Provide at least one field to update.")
        return self._put(f"/cards/{card_id}/checkItem/{check_item_id}", **params)

    def delete_check_item(self, checklist_id: str, check_item_id: str) -> None:
        """Delete a check item via DELETE /checklists/{id}/checkItems/{idCheckItem}."""
        self._delete(f"/checklists/{checklist_id}/checkItems/{check_item_id}")
