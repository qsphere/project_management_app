"""Settings → Connections tab (named Trello credentials)."""

from __future__ import annotations

import streamlit as st

from constants.links import TRELLO_REST_API_GUIDE_URL
from constants.styles import CONNECTIONS_CSS
from services.auth import AuthError
from services.config import list_trello_connections
from ui.component.auth import current_user
from ui.component.connection_dialog import (
    open_add_connection_dialog,
    render_connection_dialog,
)
from ui.component.connection_list import render_connection_list


def render_settings_connections_tab() -> None:
    st.markdown(CONNECTIONS_CSS, unsafe_allow_html=True)
    st.markdown(
        f'<p class="connections-kicker">Trello API credentials used to sync '
        "boards, lists, and cards. Need a key or token? See the "
        f'<a href="{TRELLO_REST_API_GUIDE_URL}" target="_blank" rel="noopener">'
        "Trello REST API guide</a>.</p>",
        unsafe_allow_html=True,
    )

    user = current_user()
    if user is None:
        st.info("Sign in to view or edit Trello API credentials.")
        return

    try:
        connections = list_trello_connections(user["id"])
    except AuthError as exc:
        st.error(str(exc))
        return

    count_col, add_col = st.columns([4, 1], vertical_alignment="center")
    with count_col:
        st.markdown(
            f'<p class="conn-count">{len(connections)} saved connection(s)</p>',
            unsafe_allow_html=True,
        )
    with add_col:
        if st.button(
            "Add connection",
            type="primary",
            width="stretch",
            key="conn_add_btn",
        ):
            open_add_connection_dialog()

    render_connection_list(user["id"], connections)
    render_connection_dialog(user["id"])
