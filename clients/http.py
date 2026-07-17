"""Strict HTTP transport for the Trello REST API.

Only this package should call ``requests`` against Trello. Auth is always
query params ``key`` + ``token``. Never log URLs/params that include secrets.
"""

from __future__ import annotations

from typing import Any

import requests

TRELLO_API = "https://api.trello.com/1"


def raise_for_status(response: requests.Response) -> None:
    """Raise HTTPError with status + body, without embedding key/token query params."""
    if response.ok:
        return
    detail = (response.text or "").strip() or response.reason
    raise requests.HTTPError(
        f"{response.status_code} {response.reason}"
        + (f": {detail}" if detail else ""),
        response=response,
    )



class TrelloHttp:
    """Session + auth + verb helpers. Subclass for resource methods."""

    def __init__(self, api_key: str, token: str, board_id: str):
        self.api_key = api_key
        self.token = token
        self.board_id = board_id
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self._lists_by_name: dict[str, str] | None = None
        self._labels_by_name: dict[str, str] | None = None
        self._members_by_name: dict[str, str] | None = None

    def _auth_params(self, **extra: Any) -> dict[str, Any]:
        """Trello auth is always query params: key + token."""
        params = {"key": self.api_key, "token": self.token}
        params.update(extra)
        return params

    def _get(self, path: str, **params: Any) -> Any:
        response = self.session.get(
            f"{TRELLO_API}{path}",
            params=self._auth_params(**params),
            timeout=30,
        )
        raise_for_status(response)
        return response.json()

    def _post(
        self,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        **params: Any,
    ) -> Any:
        """
        POST to the Trello REST API.

        Auth stays in the query string. Card/create fields may be query params
        or a JSON body (docs: POST /cards).
        """
        response = self.session.post(
            f"{TRELLO_API}{path}",
            params=self._auth_params(**params),
            json=json_body,
            timeout=30,
        )
        raise_for_status(response)
        return response.json()

    def _put(self, path: str, **params: Any) -> Any:
        response = self.session.put(
            f"{TRELLO_API}{path}",
            params=self._auth_params(**params),
            timeout=30,
        )
        raise_for_status(response)
        return response.json()

    def _delete(self, path: str, **params: Any) -> Any:
        response = self.session.delete(
            f"{TRELLO_API}{path}",
            params=self._auth_params(**params),
            timeout=30,
        )
        raise_for_status(response)
        if response.status_code == 204 or not (response.text or "").strip():
            return None
        return response.json()
