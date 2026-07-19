#!/usr/bin/env python3
"""
Streamlit UI entry: initiative dashboard, cards, labels, and settings.

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
from ui.component.auth import current_user, render_auth_bar
from ui.component.no_connection import render_no_connection_empty
from ui.component.sidebar import render_sidebar
from ui.component.trello_config_state import (
    signed_in_without_connection,
    sync_trello_config_session,
)
from ui.views.cards import render_cards_page
from ui.views.dashboard import render_dashboard_page
from ui.views.labels import render_labels_page
from ui.views.settings import render_settings_page

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

signed_in = current_user() is not None
# Signed-out users only see Dashboard; Cards, Labels, Settings need auth.
_SIGNED_IN_ONLY = frozenset({"Cards", "Labels", "Settings"})
nav_pages = (
    list(PAGES) if signed_in else [p for p in PAGES if p not in _SIGNED_IN_ONLY]
)

# Horizontal radio keeps labels visible (tabs/pills were collapsing to a blank bar).
if "main_nav" not in st.session_state:
    st.session_state.main_nav = "Dashboard"
# Migrate sessions that still have old nav values.
elif st.session_state.main_nav == "Import cards":
    st.session_state.main_nav = "Cards"
elif st.session_state.main_nav in (
    "Configuration",
    "Connections",
    "Connection",
):
    st.session_state.main_nav = "Settings"
# Signed-out users cannot stay on auth-gated pages.
if st.session_state.main_nav not in nav_pages:
    st.session_state.main_nav = "Dashboard"

nav_col, auth_col = st.columns([5, 2], vertical_alignment="center")
with nav_col:
    page = st.radio(
        "Pages",
        options=nav_pages,
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
            "Connect with API key, token, and board ID on the Settings "
            "page (or in `.env`) to view the initiative dashboard."
        )
    else:
        render_dashboard_page(client)
elif page == "Cards" and signed_in:
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
elif page == "Labels" and signed_in:
    if no_connection:
        render_no_connection_empty("Labels")
    elif client is None:
        st.info(
            "Connect with API key, token, and board ID on the Settings "
            "page (or in `.env`) to manage labels."
        )
    else:
        render_labels_page(client)
elif page == "Settings" and signed_in:
    render_settings_page()
