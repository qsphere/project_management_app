"""Dialogs for add/rename taxonomy dimensions."""

from __future__ import annotations

import streamlit as st

from services.auth import AuthError
from services.taxonomy import create_dimension, rename_dimension

_DIM_OPEN = "tax_dim_dialog_open"
_DIM_EDIT_KEY = "tax_dim_edit_key"
_DIM_NAME = "tax_dim_form_name"


def open_add_dimension_dialog() -> None:
    st.session_state[_DIM_OPEN] = True
    st.session_state.pop(_DIM_EDIT_KEY, None)
    st.session_state[_DIM_NAME] = ""
    st.rerun()


def open_rename_dimension_dialog(dimension: dict) -> None:
    st.session_state[_DIM_OPEN] = True
    st.session_state[_DIM_EDIT_KEY] = dimension["dimension_key"]
    st.session_state[_DIM_NAME] = dimension.get("name", "")
    st.rerun()


def _close_dim() -> None:
    st.session_state.pop(_DIM_OPEN, None)
    st.session_state.pop(_DIM_EDIT_KEY, None)
    st.session_state.pop(_DIM_NAME, None)


def render_taxonomy_dialogs(*, user_id: int | str, dimensions: list[dict]) -> None:
    _ = dimensions
    if st.session_state.get(_DIM_OPEN):
        _render_dimension_dialog(user_id)


def _render_dimension_dialog(user_id: int | str) -> None:
    editing = _DIM_EDIT_KEY in st.session_state
    title = "Rename dimension" if editing else "Add dimension"

    @st.dialog(title, width="small", on_dismiss=_close_dim)
    def _dialog() -> None:
        st.text_input("NAME", key=_DIM_NAME)
        ok = bool(str(st.session_state.get(_DIM_NAME, "")).strip())
        _, cancel_col, save_col = st.columns([2, 1, 1])
        with cancel_col:
            if st.button("Cancel", width="stretch", key="tax_dim_cancel"):
                _close_dim()
                st.rerun()
        with save_col:
            if st.button(
                "Save",
                type="primary",
                width="stretch",
                disabled=not ok,
                key="tax_dim_save",
            ):
                _save_dimension(user_id, editing)

    _dialog()


def _save_dimension(user_id: int | str, editing: bool) -> None:
    try:
        name = st.session_state[_DIM_NAME]
        if editing:
            rename_dimension(
                user_id=user_id,
                dimension_key=st.session_state[_DIM_EDIT_KEY],
                name=name,
            )
        else:
            create_dimension(user_id=user_id, name=name)
        _close_dim()
        st.rerun()
    except AuthError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Could not save dimension: {exc}")
