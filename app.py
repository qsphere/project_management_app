#!/usr/bin/env python3
"""
Streamlit UI entry: initiative dashboard, cards, labels, and connection.

Run from the project root:
  streamlit run app.py

Streamlit adds this file's directory (project root) to sys.path, so
`ui/`, `constants/`, `functions/`, and `services/` import as packages.

"""

from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from constants.pages import PAGES
from constants.styles import NAV_CSS
from functions.env import SCRIPT_DIR
from ui.component.auth import render_auth_bar
from ui.component.no_connection import render_no_connection_empty
from ui.component.sidebar import render_sidebar
from ui.component.trello_config_state import (
    signed_in_without_connection,
    sync_trello_config_session,
)
from ui.views.cards import render_cards_page
from ui.views.connections import render_connections_page
from ui.views.dashboard import render_dashboard_page
from ui.views.labels import render_labels_page

load_dotenv(SCRIPT_DIR / ".env")

st.set_page_config(
    page_title="Initiative Dashboard",
    layout="wide",
)

# Force page-nav labels to stay readable (Streamlit tabs/segmented can collapse).
st.markdown(NAV_CSS, unsafe_allow_html=True)

sync_trello_config_session()

(
    api_key,
    token,
    board_id,
    list_options,
    selected_list_id,
    client,
    delay,
) = render_sidebar()

# Horizontal radio keeps labels visible (tabs/pills were collapsing to a blank bar).
if "main_nav" not in st.session_state:
    st.session_state.main_nav = "Dashboard"
# Migrate sessions that still have old nav values.
elif st.session_state.main_nav == "Import cards":
    st.session_state.main_nav = "Cards"
elif st.session_state.main_nav in ("Configuration", "Connections"):
    st.session_state.main_nav = "Connection"

nav_col, auth_col = st.columns([5, 2], vertical_alignment="center")
with nav_col:
    page = st.radio(
        "Pages",
        options=list(PAGES),
        key="main_nav",
        horizontal=True,
        label_visibility="collapsed",
    )
with auth_col:
    render_auth_bar()

no_connection = signed_in_without_connection()

if page == "Dashboard":
    if no_connection:
        render_no_connection_empty("Dashboard")
    elif client is None:
        st.info(
            "Connect with API key, token, and board ID on the Connection "
            "page (or in `.env`) to view the initiative dashboard."
        )
    else:
        render_dashboard_page(client)
elif page == "Cards":
    if no_connection:
        render_no_connection_empty("Cards")
    else:
        render_cards_page(
            client=client,
            api_key=api_key,
            token=token,
            board_id=board_id,
            list_options=list_options,
            selected_list_id=selected_list_id,
            delay=delay,
        )
elif page == "Labels":
    if no_connection:
        render_no_connection_empty("Labels")
    elif client is None:
        st.info(
            "Connect with API key, token, and board ID on the Connection "
            "page (or in `.env`) to manage labels."
        )
    else:
        render_labels_page(client)
elif page == "Connection":
    render_connections_page()
