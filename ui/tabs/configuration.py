"""Configuration tab: edit Initiative and Status entity mappings."""

from __future__ import annotations

from html import escape

import streamlit as st

from constants.config_styles import CONFIGURATION_CSS
from services.auth import AuthError
from services.entity_config import list_entity_configurations
from ui.component.auth import current_user
from ui.component.configuration_dialog import (
    open_edit_configuration_dialog,
    render_configuration_dialog,
)


def render_configuration_tab() -> None:
    st.markdown(CONFIGURATION_CSS, unsafe_allow_html=True)
    st.markdown(
        '<p class="config-kicker">Define the entity types used across the '
        "dashboard, such as Initiative and Status.</p>",
        unsafe_allow_html=True,
    )

    user = current_user()
    if user is None:
        st.info("Sign in to view or edit dashboard configurations.")
        return

    try:
        configs = list_entity_configurations(user["id"])
    except AuthError as exc:
        st.error(str(exc))
        return

    st.markdown(
        f'<p class="config-count">{len(configs)} configuration(s)</p>',
        unsafe_allow_html=True,
    )
    for config in configs:
        _render_card(config)
    render_configuration_dialog(user["id"])


def _render_card(config: dict) -> None:
    name = escape(config.get("name") or "Untitled")
    maps_to = escape(config.get("maps_to") or "—")
    desc = escape(config.get("description") or "")
    with st.container(border=True):
        left, right = st.columns([5, 1], vertical_alignment="center")
        with left:
            st.markdown(
                f'<p class="config-card-title">{name}</p>'
                f'<span class="config-badge">{maps_to}</span>'
                f'<p class="config-card-desc">{desc}</p>',
                unsafe_allow_html=True,
            )
        with right:
            if st.button(
                "Edit",
                key=f"config_edit_{config['entity_key']}",
                width="stretch",
            ):
                open_edit_configuration_dialog(config)
