"""Trello label color palette (30 official API colors) + dashboard CSS inject."""

from __future__ import annotations

import streamlit as st

from constants.colors import COLOR_SWATCH, LABEL_COLORS, PALETTE_HUES
from constants.styles import DASHBOARD_CSS

_SHADE_SUFFIXES = ("_light", "", "_dark")


def inject_dashboard_css() -> None:
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)


def _ensure_color(state_key: str, default: str) -> str:
    current = st.session_state.get(state_key)
    if current not in LABEL_COLORS:
        st.session_state[state_key] = default if default in LABEL_COLORS else "green"
    return st.session_state[state_key]


def _swatch_button_css(state_key: str, selected: str) -> str:
    rules: list[str] = []
    for name in LABEL_COLORS:
        hex_color = COLOR_SWATCH[name]
        border = "#111827" if name == selected else "rgba(15, 23, 42, 0.12)"
        width = "2.5px" if name == selected else "1px"
        rules.append(
            f"div.st-key-{state_key}_sw_{name} button{{"
            f"background-color:{hex_color}!important;"
            f"border:{width} solid {border}!important;"
            f"border-radius:0.45rem!important;"
            f"min-height:2rem!important;height:2rem!important;"
            f"padding:0!important;box-shadow:none!important;"
            f"color:transparent!important;}}"
        )
    return "<style>" + "".join(rules) + "</style>"


def render_color_selector(state_key: str, *, default: str = "green") -> str:
    """Clickable Trello label color grid. Returns an official color name."""
    selected = _ensure_color(state_key, default)
    st.markdown(_swatch_button_css(state_key, selected), unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#6b7280;font-size:0.72rem;font-weight:650;'
        "letter-spacing:0.06em;text-transform:uppercase;"
        'margin:0.35rem 0 0.45rem;">Color</p>',
        unsafe_allow_html=True,
    )

    for suffix in _SHADE_SUFFIXES:
        cols = st.columns(len(PALETTE_HUES), gap="small")
        for col, hue in zip(cols, PALETTE_HUES):
            name = f"{hue}{suffix}" if suffix else hue
            with col:
                if st.button(
                    "·",
                    key=f"{state_key}_sw_{name}",
                    help=name,
                    width="stretch",
                ):
                    st.session_state[state_key] = name
                    st.rerun()

    return st.session_state[state_key]
