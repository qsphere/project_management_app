"""Empty states when signed in with no active Trello connection."""

from __future__ import annotations

from html import escape

import streamlit as st

from constants.empty_state import NO_CONNECTION_CSS
from ui.component.auth import current_user
from ui.component.connection_dialog import open_add_connection_dialog
from ui.component.footer import render_page_footer

_EMPTY_STATES = {
    "Dashboard": {
        "page_title": "Dashboard",
        "page_sub": "Quick overview of your board stats.",
        "title": "No items yet",
        "body": "Add a connection to start syncing data from Trello.",
        "button": "Add connection",
    },
    "Cards": {
        "page_title": "Cards",
        "page_sub": (
            "Browse and edit cards on the board, or import new ones "
            "from a spreadsheet."
        ),
        "title": "No cards yet",
        "body": "Add a connection to start syncing cards from Trello.",
        "button": "Add connection",
    },
    "Labels": {
        "page_title": "Labels",
        "page_sub": "Select labels from the board to sync.",
        "title": "No connection yet",
        "body": "Add a connection to start syncing labels from Trello.",
        "button": "Add connection",
    },
}


def go_to_add_connection() -> None:
    st.session_state.main_nav = "Connection"
    open_add_connection_dialog()


def render_no_connection_empty(page: str) -> None:
    """Render the logged-in, no-connection empty state for a main nav page."""
    st.markdown(NO_CONNECTION_CSS, unsafe_allow_html=True)
    spec = _EMPTY_STATES[page]
    if spec["page_title"]:
        st.markdown(f"## {spec['page_title']}")
        st.markdown(
            f'<p class="nc-page-sub">{escape(spec["page_sub"] or "")}</p>',
            unsafe_allow_html=True,
        )

    title = spec["title"]
    body = escape(spec["body"])
    show_btn = spec["button"] and current_user() is not None

    with st.container(border=True):
        if title:
            st.markdown(
                f'<div class="nc-inner">'
                f'<p class="nc-title">{escape(title)}</p>'
                f'<p class="nc-body">{body}</p></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="nc-inner">'
                f'<p class="nc-body nc-body-only">{body}</p></div>',
                unsafe_allow_html=True,
            )
        if show_btn:
            _, mid, _ = st.columns([1.2, 1, 1.2])
            with mid:
                if st.button(
                    spec["button"],
                    type="primary",
                    width="stretch",
                    key=f"nc_add_conn_{page}",
                ):
                    go_to_add_connection()

    render_page_footer()
