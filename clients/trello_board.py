"""Board / list / member reads and name→id resolution (Trello HTTP)."""

from __future__ import annotations

from typing import Any

import pandas as pd


class TrelloBoardMixin:
    def open_lists(self) -> list[dict[str, str]]:
        """Return open lists as [{id, name}, ...] in board order."""
        return [
            {"id": item["id"], "name": item["name"]}
            for item in self._get(f"/boards/{self.board_id}/lists", filter="open")
        ]

    def lists_by_name(self) -> dict[str, str]:
        if self._lists_by_name is None:
            self._lists_by_name = {
                item["name"].strip().lower(): item["id"] for item in self.open_lists()
            }
        return self._lists_by_name

    def board_cards(self) -> list[dict[str, Any]]:
        """
        Return open cards on the board as
        [{id, name, idList, idLabels}, ...].

        See: https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-cards-get
        """
        cards = self._get(
            f"/boards/{self.board_id}/cards",
            filter="open",
            fields="id,name,idList,idLabels",
        )
        return [
            {
                "id": item["id"],
                "name": item.get("name") or "",
                "idList": item.get("idList") or "",
                "idLabels": item.get("idLabels") or [],
            }
            for item in cards
        ]

    def board_cards_dashboard(self) -> list[dict[str, Any]]:
        """
        Return open and closed cards with fields needed for the initiative dashboard.

        Includes due/start dates, completion flags, and closed state so burndown
        and status percentages can be computed. filter=all pulls archived cards too.
        """
        cards = self._get(
            f"/boards/{self.board_id}/cards",
            filter="all",
            fields=(
                "id,name,idList,idLabels,due,start,dueComplete,"
                "dateLastActivity,closed"
            ),
        )
        return [
            {
                "id": item["id"],
                "name": item.get("name") or "",
                "idList": item.get("idList") or "",
                "idLabels": item.get("idLabels") or [],
                "due": item.get("due"),
                "start": item.get("start"),
                "dueComplete": bool(item.get("dueComplete")),
                "dateLastActivity": item.get("dateLastActivity"),
                "closed": bool(item.get("closed")),
            }
            for item in cards
        ]

    def board_cards_manage(self) -> list[dict[str, Any]]:
        """
        Return open cards on the board with fields used by the Cards Manage UI.

        See: https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-cards-get
        """
        cards = self._get(
            f"/boards/{self.board_id}/cards",
            filter="open",
            fields=(
                "id,name,desc,due,start,idList,idLabels,idMembers,"
                "shortUrl,pos,badges"
            ),
        )
        return [
            {
                "id": item["id"],
                "name": item.get("name") or "",
                "desc": item.get("desc") or "",
                "due": item.get("due"),
                "start": item.get("start"),
                "idList": item.get("idList") or "",
                "idLabels": item.get("idLabels") or [],
                "idMembers": item.get("idMembers") or [],
                "shortUrl": item.get("shortUrl") or "",
                "pos": item.get("pos"),
                "badges": item.get("badges") or {},
            }
            for item in cards
        ]

    def cards_in_list(self, list_id: str) -> list[dict[str, Any]]:
        """
        Return open cards in a list as
        [{id, name, desc, due, start, idLabels, idMembers, shortUrl, pos}, ...].

        See: https://developer.atlassian.com/cloud/trello/rest/api-group-lists/#api-lists-id-cards-get
        """
        cards = self._get(
            f"/lists/{list_id}/cards",
            fields="id,name,desc,due,start,idLabels,idMembers,shortUrl,pos",
        )
        return [
            {
                "id": item["id"],
                "name": item.get("name") or "",
                "desc": item.get("desc") or "",
                "due": item.get("due"),
                "start": item.get("start"),
                "idList": list_id,
                "idLabels": item.get("idLabels") or [],
                "idMembers": item.get("idMembers") or [],
                "shortUrl": item.get("shortUrl") or "",
                "pos": item.get("pos"),
            }
            for item in cards
        ]

    def board_members(self) -> list[dict[str, Any]]:
        """
        Return board members as [{id, fullName, username}, ...].

        Uses GET /boards/{id} with nested members:
        https://developer.atlassian.com/cloud/trello/rest/api-group-boards/#api-boards-id-get
        """
        board = self._get(
            f"/boards/{self.board_id}",
            fields="name",
            members="all",
            member_fields="id,fullName,username",
        )
        members = board.get("members") or []
        return [
            {
                "id": item["id"],
                "fullName": item.get("fullName") or "",
                "username": item.get("username") or "",
            }
            for item in members
        ]

    def members_by_name(self) -> dict[str, str]:
        """
        Map lowercased fullName and username → member id.

        Both keys point at the same id when both are present, so spreadsheet
        values can use either display name or @username.
        """
        if self._members_by_name is None:
            mapping: dict[str, str] = {}
            for item in self.board_members():
                member_id = item["id"]
                full_name = (item.get("fullName") or "").strip().lower()
                username = (item.get("username") or "").strip().lower()
                if full_name:
                    mapping[full_name] = member_id
                if username:
                    mapping[username] = member_id
            self._members_by_name = mapping
        return self._members_by_name

    def resolve_member_ids(self, assignees_value: str | None) -> list[str]:
        """
        Resolve comma-separated assignee names to board member IDs (idMembers).

        Matches against each member's fullName and username (case-insensitive).
        Raises ValueError if any name is not a member of this board.
        """
        if not assignees_value or pd.isna(assignees_value):
            return []

        member_ids: list[str] = []
        missing: list[str] = []
        seen: set[str] = set()

        for raw in str(assignees_value).split(","):
            name = raw.strip()
            if not name:
                continue
            # Allow values like "@jane" from spreadsheets.
            key = name.lstrip("@").strip().lower()
            if not key:
                continue
            member_id = self.members_by_name().get(key)
            if not member_id:
                missing.append(name)
                continue
            if member_id not in seen:
                seen.add(member_id)
                member_ids.append(member_id)

        if missing:
            available = (
                ", ".join(
                    sorted(
                        {
                            (item.get("fullName") or item.get("username") or item["id"])
                            for item in self.board_members()
                        }
                    )
                )
                or "(none)"
            )
            raise ValueError(
                f"Unknown assignee(s): {', '.join(missing)}. "
                f"Available board members: {available}"
            )
        return member_ids

    def resolve_list_id(self, list_name: str | None, default_list_id: str | None) -> str:
        if list_name:
            list_id = self.lists_by_name().get(list_name.strip().lower())
            if not list_id:
                available = ", ".join(sorted(self.lists_by_name())) or "(none)"
                raise ValueError(
                    f"List '{list_name}' not found on board. Available lists: {available}"
                )
            return list_id
        if default_list_id:
            return default_list_id
        raise ValueError(
            "No list specified. Provide a List column value, --list-id, or TRELLO_LIST_ID."
        )
