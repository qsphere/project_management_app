"""Header auth controls: Sign in / Sign up modal and Sign out."""

from __future__ import annotations

import streamlit as st

from services.auth import AuthError, create_account, sign_in

_AUTH_USER_KEY = "auth_user"
_AUTH_DIALOG_KEY = "auth_dialog_open"
_AUTH_MODE_KEY = "auth_dialog_mode"
_SIGN_IN = "Sign in"
_CREATE = "Create account"


def current_user() -> dict | None:
    return st.session_state.get(_AUTH_USER_KEY)


def _close_auth_dialog() -> None:
    st.session_state.pop(_AUTH_DIALOG_KEY, None)
    st.session_state.pop(_AUTH_MODE_KEY, None)
    st.session_state.pop("auth_mode_radio", None)


def _open_dialog(mode: str) -> None:
    st.session_state[_AUTH_DIALOG_KEY] = True
    st.session_state[_AUTH_MODE_KEY] = mode
    st.session_state["auth_mode_radio"] = mode
    st.rerun()


def _set_user(user: dict) -> None:
    st.session_state[_AUTH_USER_KEY] = user
    _close_auth_dialog()
    st.rerun()


def _sign_out() -> None:
    st.session_state.pop(_AUTH_USER_KEY, None)
    st.rerun()


def _render_sign_in_form() -> None:
    email = st.text_input(
        "Email address",
        key="auth_sign_in_email",
        placeholder="you@example.com",
    )
    password = st.text_input(
        "Password",
        key="auth_sign_in_password",
        type="password",
    )
    if st.button("Sign in", type="primary", width="stretch", key="auth_sign_in_btn"):
        try:
            _set_user(sign_in(email=email, password=password))
        except AuthError as exc:
            st.error(str(exc))


def _render_create_form() -> None:
    full_name = st.text_input(
        "Full name",
        key="auth_create_name",
        placeholder="Jordan Lee",
    )
    email = st.text_input(
        "Email address",
        key="auth_create_email",
        placeholder="you@example.com",
    )
    password = st.text_input(
        "Password",
        key="auth_create_password",
        type="password",
        placeholder="At least 8 characters",
    )
    confirm = st.text_input(
        "Confirm password",
        key="auth_create_confirm",
        type="password",
        placeholder="Re-enter password",
    )
    if st.button(
        "Create account",
        type="primary",
        width="stretch",
        key="auth_create_btn",
    ):
        if password != confirm:
            st.error("Passwords do not match.")
            return
        try:
            _set_user(
                create_account(
                    full_name=full_name,
                    email=email,
                    password=password,
                )
            )
        except AuthError as exc:
            st.error(str(exc))


def _open_auth_dialog() -> None:
    @st.dialog("Account", width="small", on_dismiss=_close_auth_dialog)
    def _dialog() -> None:
        mode = st.radio(
            "Auth mode",
            options=[_SIGN_IN, _CREATE],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_mode_radio",
        )
        if mode == _SIGN_IN:
            _render_sign_in_form()
        else:
            _render_create_form()

    _dialog()


def render_auth_bar() -> None:
    """Render Sign in / Sign out; open the auth modal when needed."""
    user = current_user()
    if user is None:
        with st.container(horizontal=True, horizontal_alignment="right"):
            if st.button(
                "Sign in or create account",
                type="secondary",
                key="auth_header_sign_up",
            ):
                _open_dialog(_SIGN_IN)
    else:
        with st.container(horizontal=True, horizontal_alignment="right"):
            if st.button("Sign out", type="secondary", key="auth_header_sign_out"):
                _sign_out()

    if st.session_state.get(_AUTH_DIALOG_KEY):
        _open_auth_dialog()
