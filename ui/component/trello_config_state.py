"""Session helpers for active Trello connection (Streamlit-only)."""

from __future__ import annotations

import streamlit as st

from services.config import (
    credentials_from_connection,
    env_trello_config,
    list_trello_connections,
)

_ACTIVE_ID_KEY = "active_connection_id"
_ACTIVE_CREDS_KEY = "trello_config"
# Must match ui.component.auth._AUTH_USER_KEY
_AUTH_USER_KEY = "auth_user"
FORM_KEYS = {
    "name": "conn_form_name",
    "api_key": "conn_form_api_key",
    "token": "conn_form_token",
    "board_id": "conn_form_board_id",
    "list_id": "conn_form_list_id",
}


def clear_trello_config_session() -> None:
    st.session_state.pop(_ACTIVE_ID_KEY, None)
    st.session_state.pop(_ACTIVE_CREDS_KEY, None)
    for key in FORM_KEYS.values():
        st.session_state.pop(key, None)
    st.session_state.pop("conn_dialog_open", None)
    st.session_state.pop("conn_dialog_mode", None)
    st.session_state.pop("conn_edit_id", None)
    st.session_state.pop("conn_delete_id", None)


def _empty_credentials() -> dict[str, str]:
    return {key: "" for key in ("api_key", "token", "board_id", "list_id")}


def set_active_connection(conn: dict | None) -> None:
    if conn is None:
        st.session_state.pop(_ACTIVE_ID_KEY, None)
        # Signed-in users must use a saved connection; do not fall back to secrets.
        if st.session_state.get(_AUTH_USER_KEY) is not None:
            st.session_state[_ACTIVE_CREDS_KEY] = _empty_credentials()
        else:
            st.session_state[_ACTIVE_CREDS_KEY] = env_trello_config()
        return
    st.session_state[_ACTIVE_ID_KEY] = conn["id"]
    st.session_state[_ACTIVE_CREDS_KEY] = credentials_from_connection(conn)


def sync_trello_config_session() -> dict[str, str]:
    """Resolve active credentials from saved connections or secrets."""
    defaults = env_trello_config()
    user = st.session_state.get(_AUTH_USER_KEY)
    if user is None:
        st.session_state[_ACTIVE_CREDS_KEY] = defaults
        return dict(defaults)

    try:
        connections = list_trello_connections(user["id"])
    except Exception:
        # Signed-in: no Neon connections available → empty, not secrets.
        set_active_connection(None)
        return dict(st.session_state[_ACTIVE_CREDS_KEY])

    if not connections:
        set_active_connection(None)
        return dict(st.session_state[_ACTIVE_CREDS_KEY])

    active_id = st.session_state.get(_ACTIVE_ID_KEY)
    chosen = next((c for c in connections if c["id"] == active_id), None)
    if chosen is None:
        chosen = connections[0]
    set_active_connection(chosen)
    return dict(st.session_state[_ACTIVE_CREDS_KEY])


def active_connection_id() -> int | None:
    return st.session_state.get(_ACTIVE_ID_KEY)


def signed_in_without_connection() -> bool:
    """True when the user is signed in and has no saved Trello connection."""
    return (
        st.session_state.get(_AUTH_USER_KEY) is not None
        and active_connection_id() is None
    )
