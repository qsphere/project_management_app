"""Labels page metrics and board label table."""

from __future__ import annotations

from html import escape

import streamlit as st

from clients import TrelloClient
from constants.colors import COLOR_SWATCH
from services import delete_label, label_dashboard_rows, load_label_dashboard
from ui.component.label_crud import open_edit_label_dialog

_DELETE_ID = "label_table_delete_id"


def render_label_overview(client: TrelloClient) -> None:
    try:
        labels, cards, lists = load_label_dashboard(client)
    except Exception as exc:
        st.error(f"Could not load labels: {exc}")
        return

    dashboard = label_dashboard_rows(labels, cards, lists) if labels else []
    applications = sum(item["total"] for item in dashboard)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f'<p class="labels-metric-label">Labels</p>'
            f'<p class="labels-metric-value">{len(dashboard)}</p>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<p class="labels-metric-label">Open cards</p>'
            f'<p class="labels-metric-value">{len(cards)}</p>',
            unsafe_allow_html=True,
        )
    with m3:
        title_col, info_col = st.columns([6, 1], vertical_alignment="center")
        with title_col:
            st.markdown(
                '<p class="labels-metric-label">Label applications</p>',
                unsafe_allow_html=True,
            )
        with info_col:
            with st.popover(
                "",
                icon=":material/info:",
                help="What this means",
                key="label_apps_info",
            ):
                st.markdown(
                    "Total times labels are attached to open cards. "
                    "A card with 3 labels counts as **3** applications, "
                    "so this can be higher than Open cards."
                )
        st.markdown(
            f'<p class="labels-metric-value">{applications}</p>',
            unsafe_allow_html=True,
        )

    if st.session_state.get(_DELETE_ID) is not None:
        _render_delete_confirm(client, dashboard)
        return

    if not dashboard:
        st.info("This board has no labels yet. Create one with + New label.")
        return

    h_label, h_cards, h_actions = st.columns([4, 1, 1.1])
    h_label.markdown(
        '<p class="labels-metric-label">Label</p>',
        unsafe_allow_html=True,
    )
    h_cards.markdown(
        '<p class="labels-metric-label">Cards</p>',
        unsafe_allow_html=True,
    )
    h_actions.markdown(
        '<p class="labels-metric-label">Actions</p>',
        unsafe_allow_html=True,
    )
    st.divider()
    for item in dashboard:
        _render_row(item)


def _render_row(item: dict) -> None:
    color = item.get("color") or "(none)"
    swatch = COLOR_SWATCH.get(color, "#DFE1E6")
    name = escape(item.get("name") or "(unnamed)")
    left, cards_col, actions = st.columns([4, 1, 1.1], vertical_alignment="center")
    with left:
        st.markdown(
            f'<div class="labels-row-name">'
            f'<span class="labels-swatch" style="background:{swatch};"></span>'
            f"<span>{name}</span></div>",
            unsafe_allow_html=True,
        )
    with cards_col:
        st.markdown(
            f'<p class="labels-row-cards">{item["total"]}</p>',
            unsafe_allow_html=True,
        )
    with actions:
        edit_col, del_col = st.columns(2)
        if edit_col.button(
            ":material/edit:",
            key=f"label_edit_{item['id']}",
            help="Edit label",
            width="stretch",
        ):
            open_edit_label_dialog(item)
        if del_col.button(
            ":material/delete:",
            key=f"label_del_{item['id']}",
            help="Delete label",
            width="stretch",
        ):
            st.session_state[_DELETE_ID] = item["id"]
            st.rerun()


def _render_delete_confirm(client: TrelloClient, dashboard: list[dict]) -> None:
    label_id = st.session_state[_DELETE_ID]
    label = next((item for item in dashboard if item["id"] == label_id), None)
    name = (label or {}).get("name") or "this label"
    st.warning(f'Delete "{name}"? This cannot be undone.')
    cancel_col, confirm_col = st.columns(2)
    if cancel_col.button("Cancel", key="label_table_delete_cancel", width="stretch"):
        st.session_state.pop(_DELETE_ID, None)
        st.rerun()
    if confirm_col.button(
        "Delete",
        type="primary",
        key="label_table_delete_confirm",
        width="stretch",
    ):
        try:
            delete_label(client, label_id)
            st.session_state.pop(_DELETE_ID, None)
            st.rerun()
        except Exception as exc:
            st.error(f"Could not delete label: {exc}")
