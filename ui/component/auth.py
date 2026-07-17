"""Header auth controls: Sign in / Sign up modal and Manage account."""

from __future__ import annotations

from html import escape

import streamlit as st

from services.auth import AuthError, create_account, delete_account, sign_in
from ui.component.trello_config_state import clear_trello_config_session

_AUTH_USER_KEY = "auth_user"
_AUTH_DIALOG_KEY = "auth_dialog_open"
_AUTH_MODE_KEY = "auth_dialog_mode"
_ACCOUNT_DIALOG_KEY = "account_manage_open"
_DELETE_CONFIRM_KEY = "account_delete_confirm"
_SIGN_IN = "Sign in"
_CREATE = "Create account"


def current_user() -> dict | None:
    return st.session_state.get(_AUTH_USER_KEY)


def _close_auth_dialog() -> None:
    st.session_state.pop(_AUTH_DIALOG_KEY, None)
    st.session_state.pop(_AUTH_MODE_KEY, None)
    st.session_state.pop("auth_mode_radio", None)


def _close_account_dialog() -> None:
    st.session_state.pop(_ACCOUNT_DIALOG_KEY, None)
    st.session_state.pop(_DELETE_CONFIRM_KEY, None)


def _open_dialog(mode: str) -> None:
    st.session_state[_AUTH_DIALOG_KEY] = True
    st.session_state[_AUTH_MODE_KEY] = mode
    st.session_state["auth_mode_radio"] = mode
    st.rerun()


def _open_account_manage() -> None:
    st.session_state[_ACCOUNT_DIALOG_KEY] = True
    st.session_state.pop(_DELETE_CONFIRM_KEY, None)
    st.rerun()


def _set_user(user: dict) -> None:
    st.session_state[_AUTH_USER_KEY] = user
    _close_auth_dialog()
    st.rerun()


def _sign_out() -> None:
    st.session_state.pop(_AUTH_USER_KEY, None)
    clear_trello_config_session()
    _close_account_dialog()
    st.rerun()


def _render_sign_in_form() -> None:
    with st.form("auth_sign_in_form"):
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
        submitted = st.form_submit_button(
            "Sign in",
            type="primary",
            width="stretch",
        )
    if submitted:
        try:
            _set_user(sign_in(email=email, password=password))
        except AuthError as exc:
            st.error(str(exc))


def _render_create_form() -> None:
    with st.form("auth_create_form"):
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
        submitted = st.form_submit_button(
            "Create account",
            type="primary",
            width="stretch",
        )
    if submitted:
        # Read from session_state so dialog/fragment submit sees both values.
        password = st.session_state.get("auth_create_password", "")
        confirm = st.session_state.get("auth_create_confirm", "")
        if password != confirm:
            st.error("Passwords do not match.")
            return
        try:
            _set_user(
                create_account(
                    full_name=st.session_state.get("auth_create_name", ""),
                    email=st.session_state.get("auth_create_email", ""),
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


def _render_profile_card(user: dict) -> None:
    raw_name = (user.get("full_name") or "").strip()
    raw_email = (user.get("email") or "").strip()
    initial = escape((raw_name or raw_email or "?")[0].upper())
    name = escape(raw_name or "Account")
    email = escape(raw_email)
    st.markdown(
        f"""
        <div style="
            display:flex;align-items:center;gap:0.85rem;
            background:#f3f4f6;border-radius:0.75rem;padding:0.9rem 1rem;
            margin-bottom:1rem;
        ">
          <div style="
            width:2.5rem;height:2.5rem;border-radius:999px;background:#2563eb;
            color:#fff;font-weight:700;font-size:1.05rem;
            display:flex;align-items:center;justify-content:center;flex-shrink:0;
          ">{initial}</div>
          <div style="min-width:0;">
            <div style="font-weight:700;color:#111827;line-height:1.25;">{name}</div>
            <div style="color:#6b7280;font-size:0.9rem;line-height:1.35;">{email}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _open_account_dialog(user: dict) -> None:
    @st.dialog("Account", width="small", on_dismiss=_close_account_dialog)
    def _dialog() -> None:
        if st.session_state.get(_DELETE_CONFIRM_KEY):
            st.write(
                "This will permanently delete your account. "
                "This action cannot be undone."
            )
            cancel_col, delete_col = st.columns(2)
            if cancel_col.button(
                "Cancel", width="stretch", key="account_delete_cancel"
            ):
                st.session_state.pop(_DELETE_CONFIRM_KEY, None)
                st.rerun()
            if delete_col.button(
                "Delete",
                type="primary",
                width="stretch",
                key="account_delete_confirm_btn",
            ):
                try:
                    delete_account(user_id=user["id"])
                    st.session_state.pop(_AUTH_USER_KEY, None)
                    clear_trello_config_session()
                    _close_account_dialog()
                    st.rerun()
                except AuthError as exc:
                    st.error(str(exc))
            return

        _render_profile_card(user)
        if st.button("Sign out", type="secondary", width="stretch", key="account_sign_out"):
            _sign_out()
        if st.button(
            "Delete account",
            type="secondary",
            width="stretch",
            key="account_delete_btn",
        ):
            st.session_state[_DELETE_CONFIRM_KEY] = True
            st.rerun()

    _dialog()


def render_auth_bar() -> None:
    """Render Sign in / Manage account; open modals when needed."""
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
            if st.button(
                "Manage account",
                type="secondary",
                key="auth_header_manage_account",
            ):
                _open_account_manage()

    if st.session_state.get(_AUTH_DIALOG_KEY):
        _open_auth_dialog()
    elif user is not None and st.session_state.get(_ACCOUNT_DIALOG_KEY):
        _open_account_dialog(user)
