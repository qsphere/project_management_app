from __future__ import annotations

import streamlit as st

from constants.colors import COLOR_SWATCH, LABEL_COLORS, PALETTE_HUES
from constants.styles import DASHBOARD_CSS


def inject_dashboard_css() -> None:
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)


def render_color_selector(state_key: str, *, default: str = "red") -> str:
    """Clickable Trello label color palette. Returns a color name or '(none)'."""
    if state_key not in st.session_state:
        st.session_state[state_key] = default
    elif (
        st.session_state[state_key] != "(none)"
        and st.session_state[state_key] not in LABEL_COLORS
    ):
        st.session_state[state_key] = default

    selected = st.session_state[state_key]
    selected_hex = COLOR_SWATCH.get(selected, "#DFE1E6")

    preview_cols = st.columns([1, 4])
    with preview_cols[0]:
        st.markdown(
            f'<div style="background:{selected_hex};height:40px;border-radius:8px;'
            f'border:1px solid #dfe1e6;"></div>',
            unsafe_allow_html=True,
        )
    with preview_cols[1]:
        label = "No color" if selected == "(none)" else selected
        st.markdown(f"**Selected:** `{label}`")
        st.caption("Click a swatch in the palette to choose a Trello label color.")

    st.markdown("**Palette**")
    shade_rows = [
        ("Light", "_light"),
        ("Default", ""),
        ("Dark", "_dark"),
    ]
    label_col, *hue_cols = st.columns([1.1, *([1] * len(PALETTE_HUES))])
    label_col.caption("")
    for col, hue in zip(hue_cols, PALETTE_HUES):
        col.caption(hue[:3])

    for shade_label, suffix in shade_rows:
        label_col, *hue_cols = st.columns([1.1, *([1] * len(PALETTE_HUES))])
        label_col.caption(shade_label)
        for col, hue in zip(hue_cols, PALETTE_HUES):
            name = f"{hue}{suffix}" if suffix else hue
            hex_color = COLOR_SWATCH[name]
            is_selected = selected == name
            border = "#172B4D" if is_selected else "#dfe1e6"
            with col:
                st.markdown(
                    f'<div style="background:{hex_color};height:22px;border-radius:6px;'
                    f'border:2px solid {border};margin-bottom:2px;"></div>',
                    unsafe_allow_html=True,
                )
                if st.button(
                    "✓" if is_selected else " ",
                    key=f"{state_key}_swatch_{name}",
                    help=name,
                    width="stretch",
                ):
                    st.session_state[state_key] = name
                    st.rerun()

    none_cols = st.columns([1.1, 2, 6])
    with none_cols[1]:
        none_selected = selected == "(none)"
        st.markdown(
            f'<div style="background:#DFE1E6;height:22px;border-radius:6px;'
            f'border:2px solid {"#172B4D" if none_selected else "#dfe1e6"};'
            f'margin-bottom:2px;"></div>',
            unsafe_allow_html=True,
        )
        if st.button(
            "No color",
            key=f"{state_key}_none",
            width="stretch",
            type="primary" if none_selected else "secondary",
        ):
            st.session_state[state_key] = "(none)"
            st.rerun()

    return st.session_state[state_key]
