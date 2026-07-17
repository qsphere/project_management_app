from __future__ import annotations

import streamlit as st

from clients import TrelloClient
from constants.labels_styles import LABELS_CSS
from ui.component.footer import render_page_footer
from ui.component.label_crud import open_new_label_dialog, render_label_dialog
from ui.component.label_overview import render_label_overview


def render_labels_page(client: TrelloClient) -> None:
    st.markdown(LABELS_CSS, unsafe_allow_html=True)

    head_l, head_r = st.columns([4, 1], vertical_alignment="bottom")
    with head_l:
        st.markdown("## Labels")
    with head_r:
        if st.button(
            "+ New label",
            type="primary",
            width="stretch",
            key="labels_new_btn",
        ):
            open_new_label_dialog()
    st.markdown(
        '<p class="labels-kicker">All labels on this board, regardless of '
        "which list their cards sit in.</p>",
        unsafe_allow_html=True,
    )
    render_label_overview(client)
    render_label_dialog(client)
    render_page_footer()
