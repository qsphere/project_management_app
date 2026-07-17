"""Connection list: empty state and saved connection cards."""

from __future__ import annotations

from html import escape

import streamlit as st

from services.auth import AuthError
from services.config import delete_trello_connection
from ui.component.connection_dialog import open_edit_connection_dialog
from ui.component.trello_config_state import (
    active_connection_id,
    set_active_connection,
    sync_trello_config_session,
)

_DELETE_ID = "conn_delete_id"


def _mask(value: str) -> str:
    return "•••" if (value or "").strip() else "—"


def render_connection_list(user_id: int | str, connections: list[dict]) -> None:
    if st.session_state.get(_DELETE_ID) is not None:
        _render_delete_confirm(user_id, connections)
        return

    if not connections:
        st.markdown(
            '<div class="conn-empty">No connections saved yet.</div>',
            unsafe_allow_html=True,
        )
        return

    for conn in connections:
        _render_card(conn)


def _render_card(conn: dict) -> None:
    name = escape(conn.get("name") or "Untitled")
    board = escape(conn.get("board_id") or "—")
    list_id = escape(conn.get("list_id") or "—")
    meta = (
        f"KEY: {_mask(conn.get('api_key', ''))} &nbsp;&nbsp; "
        f"TOKEN: {_mask(conn.get('token', ''))} &nbsp;&nbsp; "
        f"BOARD: {board} &nbsp;&nbsp; "
        f"LIST: {list_id}"
    )
    with st.container(border=True):
        left, right = st.columns([4, 2], vertical_alignment="center")
        with left:
            st.markdown(
                f'<p class="conn-card-title">{name}</p>'
                f'<p class="conn-card-meta">{meta}</p>',
                unsafe_allow_html=True,
            )
        with right:
            edit_col, del_col = st.columns(2)
            if edit_col.button("Edit", key=f"conn_edit_{conn['id']}", width="stretch"):
                open_edit_connection_dialog(conn)
            if del_col.button(
                "Delete",
                key=f"conn_card_del_{conn['id']}",
                width="stretch",
            ):
                st.session_state[_DELETE_ID] = conn["id"]
                st.rerun()


def _render_delete_confirm(user_id: int | str, connections: list[dict]) -> None:
    conn_id = st.session_state[_DELETE_ID]
    conn = next((c for c in connections if c["id"] == conn_id), None)
    label = (conn or {}).get("name") or "this connection"
    st.warning(f'Delete "{label}"? This cannot be undone.')
    cancel_col, confirm_col = st.columns(2)
    if cancel_col.button("Cancel", key="conn_delete_cancel", width="stretch"):
        st.session_state.pop(_DELETE_ID, None)
        st.rerun()
    if confirm_col.button(
        "Delete",
        type="primary",
        key="conn_delete_confirm",
        width="stretch",
    ):
        try:
            delete_trello_connection(user_id=user_id, connection_id=conn_id)
            if active_connection_id() == conn_id:
                set_active_connection(None)
            st.session_state.pop(_DELETE_ID, None)
            sync_trello_config_session()
            st.rerun()
        except AuthError as exc:
            st.error(str(exc))
