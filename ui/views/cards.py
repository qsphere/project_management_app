from __future__ import annotations

import streamlit as st

from clients import TrelloClient
from ui.tabs.import_cards import render_import_tab
from ui.tabs.manage import render_manage_tab


def render_cards_page(
    *,
    client: TrelloClient | None,
    api_key: str,
    token: str,
    board_id: str,
    list_options: dict[str, str],
    selected_list_id: str | None,
    delay: float,
) -> None:
    st.markdown("## Cards")
    st.caption(
        "Browse and edit cards on the board, or import new ones from a spreadsheet."
    )
    tab_manage, tab_import = st.tabs(["Manage", "Import"])
    with tab_manage:
        if client is None:
            st.info(
                "Connect with API key, token, and board ID in the sidebar to manage cards."
            )
        else:
            render_manage_tab(
                client,
                list_options=list_options,
                default_list_id=selected_list_id,
                delay=delay,
            )
    with tab_import:
        st.caption(
            "Upload a spreadsheet, preview tasks, then dry-run or create Trello cards."
        )
        render_import_tab(
            api_key=api_key,
            token=token,
            board_id=board_id,
            selected_list_id=selected_list_id,
            delay=delay,
        )
