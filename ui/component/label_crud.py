"""Create / edit / delete label dialogs."""

from __future__ import annotations

import streamlit as st

from clients import TrelloClient
from constants.colors import LABEL_COLORS
from services import create_label, delete_label, update_label
from ui.component.color_selector import render_color_selector

_DIALOG_OPEN = "label_dialog_open"
_DIALOG_MODE = "label_dialog_mode"
_EDIT_ID = "label_edit_id"
_NAME_KEY = "label_dialog_name"
_COLOR_KEY = "label_dialog_color"


def open_new_label_dialog() -> None:
    st.session_state[_DIALOG_OPEN] = True
    st.session_state[_DIALOG_MODE] = "new"
    st.session_state.pop(_EDIT_ID, None)
    st.session_state[_NAME_KEY] = ""
    st.session_state[_COLOR_KEY] = "green"
    st.rerun()


def open_edit_label_dialog(label: dict) -> None:
    color = label.get("color") or "green"
    if color not in LABEL_COLORS:
        color = "green"
    st.session_state[_DIALOG_OPEN] = True
    st.session_state[_DIALOG_MODE] = "edit"
    st.session_state[_EDIT_ID] = label["id"]
    st.session_state[_NAME_KEY] = label.get("name") or ""
    st.session_state[_COLOR_KEY] = color
    st.rerun()


def _close_dialog() -> None:
    st.session_state.pop(_DIALOG_OPEN, None)
    st.session_state.pop(_DIALOG_MODE, None)
    st.session_state.pop(_EDIT_ID, None)


def render_label_dialog(client: TrelloClient) -> None:
    if not st.session_state.get(_DIALOG_OPEN):
        return

    mode = st.session_state.get(_DIALOG_MODE, "new")
    title = "Edit label" if mode == "edit" else "New label"

    @st.dialog(title, width="small", on_dismiss=_close_dialog)
    def _dialog() -> None:
        st.text_input("NAME", key=_NAME_KEY, placeholder="e.g. Bug")
        color = render_color_selector(_COLOR_KEY, default="green")
        name = str(st.session_state.get(_NAME_KEY, "")).strip()
        can_save = bool(name)

        if mode == "edit":
            _, cancel_col, delete_col, save_col = st.columns([1.2, 1, 1, 1])
        else:
            delete_col = None
            _, cancel_col, save_col = st.columns([2, 1, 1])

        with cancel_col:
            if st.button("Cancel", width="stretch", key="label_dialog_cancel"):
                _close_dialog()
                st.rerun()
        if delete_col is not None:
            with delete_col:
                if st.button("Delete", width="stretch", key="label_dialog_delete"):
                    try:
                        delete_label(client, st.session_state[_EDIT_ID])
                        _close_dialog()
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not delete label: {exc}")
        with save_col:
            if st.button(
                "Save",
                type="primary",
                width="stretch",
                disabled=not can_save,
                key="label_dialog_save",
            ):
                _save(client, mode, name, color)

    _dialog()


def _save(client: TrelloClient, mode: str, name: str, color: str) -> None:
    try:
        if mode == "edit":
            update_label(client, st.session_state[_EDIT_ID], name=name, color=color)
        else:
            create_label(client, name, color)
        _close_dialog()
        st.rerun()
    except Exception as exc:
        st.error(f"Could not save label: {exc}")
