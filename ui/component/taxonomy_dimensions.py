"""Configuration tab sections: dimensions and unmapped policy."""

from __future__ import annotations

from html import escape

import streamlit as st

from constants.taxonomy import UNMAPPED_EXCLUDE, UNMAPPED_SHOW
from services.auth import AuthError
from services.taxonomy import delete_dimension
from services.workspace import update_unmapped_policy
from ui.component.taxonomy_dialogs import (
    open_add_dimension_dialog,
    open_rename_dimension_dialog,
)


def render_unmapped_policy(*, user_id: int | str, current: str) -> None:
    st.markdown("### Unmapped lists & labels")
    st.caption(
        "When a card’s list/label has no mapping for a dimension, either "
        "group it as Unmapped or exclude it from that dimension’s charts."
    )
    choice = st.radio(
        "Unmapped policy",
        options=[UNMAPPED_SHOW, UNMAPPED_EXCLUDE],
        index=0 if current != UNMAPPED_EXCLUDE else 1,
        format_func=lambda p: (
            "Show as Unmapped" if p == UNMAPPED_SHOW else "Exclude from grouping"
        ),
        horizontal=True,
        key="tax_unmapped_policy",
        label_visibility="collapsed",
    )
    if choice != current:
        try:
            update_unmapped_policy(user_id=user_id, unmapped_policy=choice)
            st.rerun()
        except AuthError as exc:
            st.error(str(exc))


def render_dimensions_section(*, user_id: int | str, dimensions: list[dict]) -> None:
    head_l, head_r = st.columns([4, 1], vertical_alignment="center")
    with head_l:
        st.markdown("### Dimensions")
        st.caption(
            "Defaults: feature, initiative, status. Add custom dimensions as needed."
        )
    with head_r:
        if st.button("Add", key="tax_dim_add", width="stretch"):
            open_add_dimension_dialog()

    for dim in dimensions:
        name = escape(dim.get("name") or "—")
        key = escape(dim.get("dimension_key") or "")
        badge = "Default" if dim.get("is_default") else "Custom"
        with st.container(border=True):
            left, mid, right = st.columns([4, 1, 1], vertical_alignment="center")
            with left:
                st.markdown(
                    f'<p class="config-card-title">{name}</p>'
                    f'<span class="config-badge">{badge}</span>'
                    f'<p class="config-card-desc">key: {key}</p>',
                    unsafe_allow_html=True,
                )
            with mid:
                if st.button(
                    "Rename",
                    key=f"tax_dim_rename_{dim['dimension_key']}",
                    width="stretch",
                ):
                    open_rename_dimension_dialog(dim)
            with right:
                if not dim.get("is_default"):
                    if st.button(
                        "Delete",
                        key=f"tax_dim_del_{dim['dimension_key']}",
                        width="stretch",
                    ):
                        try:
                            delete_dimension(
                                user_id=user_id,
                                dimension_key=dim["dimension_key"],
                            )
                            st.rerun()
                        except AuthError as exc:
                            st.error(str(exc))
