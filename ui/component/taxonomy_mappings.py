"""Configuration tab: dimension → Trello field mapping radios."""

from __future__ import annotations

import streamlit as st

from constants.taxonomy import (
    SOURCE_TYPE_LABELS,
    SOURCE_TYPE_LABELS_UI,
    SOURCE_TYPES,
)
from functions.taxonomy import dimension_source_map
from services.auth import AuthError
from services.taxonomy import set_dimension_source


def render_mappings_section(
    *,
    user_id: int | str,
    dimensions: list[dict],
    mappings: list[dict],
) -> None:
    st.markdown("### Mappings")
    st.caption(
        "Choose which Trello field each dimension pulls its values from. "
        "Cards use the field’s raw names as values; the dashboard groups by them."
    )
    if not dimensions:
        st.info("Add a dimension first, then map it to a Trello field.")
        return

    sources = dimension_source_map(mappings)
    for dim in dimensions:
        key = str(dim["dimension_key"])
        name = str(dim.get("name") or key)
        current = sources.get(key, SOURCE_TYPE_LABELS)
        index = (
            list(SOURCE_TYPES).index(current)
            if current in SOURCE_TYPES
            else list(SOURCE_TYPES).index(SOURCE_TYPE_LABELS)
        )
        label_col, radio_col = st.columns([1.2, 4], vertical_alignment="center")
        with label_col:
            st.markdown(f"**{name}**")
        with radio_col:
            choice = st.radio(
                name,
                options=list(SOURCE_TYPES),
                index=index,
                format_func=lambda s: SOURCE_TYPE_LABELS_UI[s].upper(),
                horizontal=True,
                key=f"tax_map_src_{key}",
                label_visibility="collapsed",
            )
        if choice != current:
            try:
                set_dimension_source(
                    user_id=user_id, dimension_key=key, source_type=choice
                )
                st.rerun()
            except AuthError as exc:
                st.error(str(exc))
