"""Card create / update / delete (Trello HTTP)."""

from __future__ import annotations

from typing import Any


class TrelloCardsMixin:
    def create_card(
        self,
        *,
        name: str,
        id_list: str,
        desc: str = "",
        due: str | None = None,
        start: str | None = None,
        pos: str | float | None = None,
        id_labels: list[str] | None = None,
        id_members: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a card via POST /cards.

        See: https://developer.atlassian.com/cloud/trello/rest/api-group-cards/#api-cards-post

        Required: idList. Optional: name, desc, due, start, pos, idLabels, idMembers.
        Fields are sent as a JSON body; key/token remain query params.
        """
        body: dict[str, Any] = {
            "idList": id_list,
            "name": name,
            "desc": desc or "",
        }
        if due:
            body["due"] = due
        if start:
            body["start"] = start
        if pos is not None and pos != "":
            body["pos"] = pos
        if id_labels:
            body["idLabels"] = id_labels
        if id_members:
            body["idMembers"] = id_members
        return self._post("/cards", json_body=body)

    def update_card(
        self,
        card_id: str,
        *,
        name: str | None = None,
        desc: str | None = None,
        due: str | None = None,
        start: str | None = None,
        id_list: str | None = None,
        pos: str | float | None = None,
        id_labels: list[str] | None = None,
        id_members: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Update a card via PUT /cards/{id}.

        Pass due='' or start='' to clear those dates. Only provided fields are sent.
        See: https://developer.atlassian.com/cloud/trello/rest/api-group-cards/#api-cards-id-put
        """
        params: dict[str, Any] = {}
        if name is not None:
            params["name"] = name
        if desc is not None:
            params["desc"] = desc
        if due is not None:
            params["due"] = due if due else "null"
        if start is not None:
            params["start"] = start if start else "null"
        if id_list is not None:
            params["idList"] = id_list
        if pos is not None and pos != "":
            params["pos"] = pos
        if id_labels is not None:
            params["idLabels"] = ",".join(id_labels)
        if id_members is not None:
            params["idMembers"] = ",".join(id_members)
        if not params:
            raise ValueError("Provide at least one field to update.")
        return self._put(f"/cards/{card_id}", **params)

    def delete_card(self, card_id: str) -> None:
        """Delete a card via DELETE /cards/{id}."""
        self._delete(f"/cards/{card_id}")
