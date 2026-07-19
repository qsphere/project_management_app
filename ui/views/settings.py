"""Settings page: Connections and Configuration tabs."""

from __future__ import annotations

import streamlit as st

from constants.styles import CONNECTIONS_CSS
from ui.component.footer import render_page_footer
from ui.tabs.configuration import render_configuration_tab
from ui.tabs.settings_connections import render_settings_connections_tab


def render_settings_page() -> None:
    st.markdown(CONNECTIONS_CSS, unsafe_allow_html=True)
    st.markdown("## Settings")
    st.markdown(
        '<p class="connections-kicker">Manage Trello connections and '
        "taxonomy mappings. Only signed-in users can view or edit "
        "these.</p>",
        unsafe_allow_html=True,
    )

    connections_tab, configuration_tab = st.tabs(
        ["Connections", "Configuration"]
    )
    with connections_tab:
        render_settings_connections_tab()
    with configuration_tab:
        render_configuration_tab()

    render_page_footer()
