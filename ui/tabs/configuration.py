"""Configuration tab: taxonomy dimensions, mappings, and import/export."""

from __future__ import annotations

import streamlit as st

from constants.config_styles import CONFIGURATION_CSS
from services.auth import AuthError
from services.taxonomy import list_dimensions, list_mappings
from services.workspace import ensure_personal_workspace
from ui.component.auth import current_user
from ui.component.taxonomy_dialogs import render_taxonomy_dialogs
from ui.component.taxonomy_dimensions import (
    render_dimensions_section,
    render_unmapped_policy,
)
from ui.component.taxonomy_import_export import render_import_export
from ui.component.taxonomy_mappings import render_mappings_section


def render_configuration_tab() -> None:
    st.markdown(CONFIGURATION_CSS, unsafe_allow_html=True)
    st.markdown(
        '<p class="config-kicker">Map each taxonomy dimension to a Trello '
        "field (cards, lists, labels, or boards). Raw field names become "
        "dashboard values. Mappings are shared across boards in your "
        "workspace.</p>",
        unsafe_allow_html=True,
    )

    user = current_user()
    if user is None:
        st.info("Sign in to view or edit taxonomy mappings.")
        return

    user_id = user["id"]
    try:
        workspace = ensure_personal_workspace(user_id)
        dimensions = list_dimensions(user_id)
        mappings = list_mappings(user_id)
    except AuthError as exc:
        st.error(str(exc))
        return

    render_unmapped_policy(
        user_id=user_id, current=workspace.get("unmapped_policy") or "show"
    )
    st.divider()
    render_dimensions_section(user_id=user_id, dimensions=dimensions)
    st.divider()
    render_mappings_section(
        user_id=user_id, dimensions=dimensions, mappings=mappings
    )
    st.divider()
    render_import_export(user_id=user_id)
    render_taxonomy_dialogs(user_id=user_id, dimensions=dimensions)
