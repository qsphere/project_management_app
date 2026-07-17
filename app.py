#!/usr/bin/env python3
"""
Streamlit UI entry: initiative dashboard, cards, and labels.

Run from the project root:
  streamlit run app.py

Streamlit adds this file's directory (project root) to sys.path, so
`ui/`, `constants/`, `functions/`, and `services/` import as packages.

"""

from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from ui.component.auth import render_auth_bar
from ui.component.sidebar import render_sidebar
from ui.views.cards import render_cards_page
from ui.views.dashboard import render_dashboard_page
from ui.views.labels import render_labels_page
from constants.pages import PAGES
from constants.styles import NAV_CSS
from functions.env import SCRIPT_DIR

load_dotenv(SCRIPT_DIR / ".env")

st.set_page_config(
    page_title="Initiative Dashboard",
    layout="wide",
)

# Force page-nav labels to stay readable (Streamlit tabs/segmented can collapse).
st.markdown(NAV_CSS, unsafe_allow_html=True)

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
# Migrate sessions that still have the old split "Import cards" nav value.
elif st.session_state.main_nav == "Import cards":
    st.session_state.main_nav = "Cards"

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

if page == "Dashboard":
    if client is None:
        st.info(
            "Connect with API key, token, and board ID in the sidebar to view "
            "the initiative dashboard."
        )
    else:
        render_dashboard_page(client)
elif page == "Cards":
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
    if client is None:
        st.info(
            "Connect with API key, token, and board ID in the sidebar to manage labels."
        )
    else:
        render_labels_page(client)
