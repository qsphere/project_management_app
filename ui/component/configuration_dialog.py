"""Add / edit entity configuration dialog."""

from __future__ import annotations

import streamlit as st

from constants.entity_config import MAPS_TO_OPTIONS
from services.auth import AuthError
from services.entity_config import update_entity_configuration

_DIALOG_OPEN = "config_dialog_open"
_EDIT_KEY = "config_edit_entity_key"
_FORM = {
    "name": "config_form_name",
    "description": "config_form_description",
    "maps_to": "config_form_maps_to",
}


def open_edit_configuration_dialog(config: dict) -> None:
    st.session_state[_DIALOG_OPEN] = True
    st.session_state[_EDIT_KEY] = config["entity_key"]
    st.session_state[_FORM["name"]] = config.get("name", "")
    st.session_state[_FORM["description"]] = config.get("description", "")
    st.session_state[_FORM["maps_to"]] = config.get("maps_to", MAPS_TO_OPTIONS[0])
    st.rerun()


def _close_dialog() -> None:
    st.session_state.pop(_DIALOG_OPEN, None)
    st.session_state.pop(_EDIT_KEY, None)
    for key in _FORM.values():
        st.session_state.pop(key, None)


def render_configuration_dialog(user_id: int | str) -> None:
    if not st.session_state.get(_DIALOG_OPEN):
        return

    @st.dialog("Edit configuration", width="small", on_dismiss=_close_dialog)
    def _dialog() -> None:
        st.text_input("NAME", key=_FORM["name"])
        st.text_area("DESCRIPTION", key=_FORM["description"], height=100)
        st.selectbox(
            "MAPS TO TRELLO COMPONENT",
            options=list(MAPS_TO_OPTIONS),
            key=_FORM["maps_to"],
        )
        name_ok = bool(str(st.session_state.get(_FORM["name"], "")).strip())
        _, cancel_col, save_col = st.columns([2, 1, 1])
        with cancel_col:
            if st.button("Cancel", width="stretch", key="config_dialog_cancel"):
                _close_dialog()
                st.rerun()
        with save_col:
            if st.button(
                "Save",
                type="primary",
                width="stretch",
                disabled=not name_ok,
                key="config_dialog_save",
            ):
                _save(user_id)

    _dialog()


def _save(user_id: int | str) -> None:
    try:
        update_entity_configuration(
            user_id=user_id,
            entity_key=st.session_state[_EDIT_KEY],
            name=st.session_state[_FORM["name"]],
            description=st.session_state[_FORM["description"]],
            maps_to=st.session_state[_FORM["maps_to"]],
        )
        _close_dialog()
        st.rerun()
    except AuthError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Could not save configuration: {exc}")
