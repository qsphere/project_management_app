from __future__ import annotations

import streamlit as st

from clients import TrelloClient
from services import connected_client
from services.auth import AuthError
from services.config import list_trello_connections
from ui.component.auth import current_user
from ui.component.trello_config_state import (
    active_connection_id,
    set_active_connection,
    sync_trello_config_session,
)


def render_sidebar() -> tuple[
    str, str, str, dict[str, str], str | None, TrelloClient | None, float
]:
    cfg = sync_trello_config_session()
    api_key = cfg.get("api_key", "")
    token = cfg.get("token", "")
    board_id = cfg.get("board_id", "")
    default_list_id = cfg.get("list_id", "")

    list_options: dict[str, str] = {}
    selected_list_id: str | None = default_list_id or None
    client: TrelloClient | None = None

    with st.sidebar:
        st.header("Connection")
        user = current_user()
        if user is not None:
            _render_connection_picker(user["id"])
            cfg = sync_trello_config_session()
            api_key = cfg.get("api_key", "")
            token = cfg.get("token", "")
            board_id = cfg.get("board_id", "")
            default_list_id = cfg.get("list_id", "")
            selected_list_id = default_list_id or None

        if api_key and token and board_id:
            try:
                client = connected_client(api_key, token, board_id)
                assert client is not None
                lists = client.open_lists()
                list_options = {item["name"]: item["id"] for item in lists}
                names = list(list_options.keys())
                default_index = 0
                if default_list_id:
                    for i, name in enumerate(names):
                        if list_options[name] == default_list_id:
                            default_index = i
                            break
                if names:
                    chosen = st.selectbox("Default list", names, index=default_index)
                    selected_list_id = list_options[chosen]
                else:
                    st.warning("No open lists found on this board.")
                st.success("Connected to board")
            except Exception as exc:
                st.error(f"Could not load board lists: {exc}")
                client = None
                selected_list_id = default_list_id or None
        else:
            st.info(
                "Add a Trello connection on the Settings page "
                "(sign in required), or set values in "
                "`.streamlit/secrets.toml`."
            )

        delay = st.slider("Delay between creates (seconds)", 0.0, 2.0, 0.25, 0.05)

    return api_key, token, board_id, list_options, selected_list_id, client, delay


def _render_connection_picker(user_id: int | str) -> None:
    try:
        connections = list_trello_connections(user_id)
    except AuthError:
        return
    if not connections:
        return
    by_id = {c["id"]: c for c in connections}
    ids = [c["id"] for c in connections]
    active_id = active_connection_id()
    index = ids.index(active_id) if active_id in by_id else 0
    chosen_id = st.selectbox(
        "Active connection",
        ids,
        index=index,
        format_func=lambda i: by_id[i]["name"],
    )
    set_active_connection(by_id[chosen_id])
