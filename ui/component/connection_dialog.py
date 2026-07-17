"""Add / edit connection dialog."""

from __future__ import annotations

import streamlit as st

from services.auth import AuthError
from services.config import create_trello_connection, update_trello_connection
from ui.component.trello_config_state import FORM_KEYS, set_active_connection

_DIALOG_OPEN = "conn_dialog_open"
_DIALOG_MODE = "conn_dialog_mode"
_EDIT_ID = "conn_edit_id"


def open_add_connection_dialog() -> None:
    st.session_state[_DIALOG_OPEN] = True
    st.session_state[_DIALOG_MODE] = "add"
    st.session_state.pop(_EDIT_ID, None)
    for key in FORM_KEYS.values():
        st.session_state.pop(key, None)
    st.rerun()


def open_edit_connection_dialog(conn: dict) -> None:
    st.session_state[_DIALOG_OPEN] = True
    st.session_state[_DIALOG_MODE] = "edit"
    st.session_state[_EDIT_ID] = conn["id"]
    st.session_state[FORM_KEYS["name"]] = conn.get("name", "")
    st.session_state[FORM_KEYS["api_key"]] = conn.get("api_key", "")
    st.session_state[FORM_KEYS["token"]] = conn.get("token", "")
    st.session_state[FORM_KEYS["board_id"]] = conn.get("board_id", "")
    st.session_state[FORM_KEYS["list_id"]] = conn.get("list_id", "")
    st.rerun()


def _close_dialog() -> None:
    st.session_state.pop(_DIALOG_OPEN, None)
    st.session_state.pop(_DIALOG_MODE, None)
    st.session_state.pop(_EDIT_ID, None)
    for key in FORM_KEYS.values():
        st.session_state.pop(key, None)


def _fields_complete() -> bool:
    return all(
        str(st.session_state.get(FORM_KEYS[k], "")).strip()
        for k in ("name", "api_key", "token", "board_id", "list_id")
    )


def render_connection_dialog(user_id: int | str) -> None:
    if not st.session_state.get(_DIALOG_OPEN):
        return

    mode = st.session_state.get(_DIALOG_MODE, "add")
    title = "Edit connection" if mode == "edit" else "Add connection"

    @st.dialog(title, width="small", on_dismiss=_close_dialog)
    def _dialog() -> None:
        st.text_input(
            "CONNECTION NAME",
            key=FORM_KEYS["name"],
            placeholder="e.g. Marketing board",
        )
        st.text_input(
            "TRELLO_API_KEY",
            key=FORM_KEYS["api_key"],
            placeholder="Enter Trello API key",
            type="password",
        )
        st.text_input(
            "TRELLO_TOKEN",
            key=FORM_KEYS["token"],
            placeholder="Enter Trello token",
            type="password",
        )
        st.text_input(
            "TRELLO_BOARD_ID",
            key=FORM_KEYS["board_id"],
            placeholder="Enter Trello board ID",
        )
        st.text_input(
            "TRELLO_LIST_ID",
            key=FORM_KEYS["list_id"],
            placeholder="Enter Trello list ID",
        )

        complete = _fields_complete()
        _, cancel_col, save_col = st.columns([2, 1, 1])
        with cancel_col:
            if st.button("Cancel", width="stretch", key="conn_dialog_cancel"):
                _close_dialog()
                st.rerun()
        with save_col:
            if st.button(
                "Save",
                type="primary",
                width="stretch",
                disabled=not complete,
                key="conn_dialog_save",
            ):
                _save(user_id, mode)

    _dialog()


def _save(user_id: int | str, mode: str) -> None:
    payload = {
        "name": st.session_state[FORM_KEYS["name"]],
        "api_key": st.session_state[FORM_KEYS["api_key"]],
        "token": st.session_state[FORM_KEYS["token"]],
        "board_id": st.session_state[FORM_KEYS["board_id"]],
        "list_id": st.session_state[FORM_KEYS["list_id"]],
    }
    try:
        if mode == "edit":
            saved = update_trello_connection(
                user_id=user_id,
                connection_id=st.session_state[_EDIT_ID],
                **payload,
            )
        else:
            saved = create_trello_connection(user_id=user_id, **payload)
        set_active_connection(saved)
        _close_dialog()
        st.rerun()
    except AuthError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Could not save connection: {exc}")
