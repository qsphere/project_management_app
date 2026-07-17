from __future__ import annotations

import streamlit as st

from services import connected_client
from clients import TrelloClient
from functions.env import env


def render_sidebar() -> tuple[
    str, str, str, dict[str, str], str | None, TrelloClient | None, float
]:
    with st.sidebar:
        st.header("Connection")
        api_key = st.text_input(
            "API key",
            value=env("TRELLO_API_KEY"),
            type="password",
            help="From https://trello.com/power-ups/admin",
        )
        token = st.text_input(
            "Token",
            value=env("TRELLO_TOKEN"),
            type="password",
        )
        board_id = st.text_input("Board ID", value=env("TRELLO_BOARD_ID"))

        default_list_id = env("TRELLO_LIST_ID")
        list_options: dict[str, str] = {}
        selected_list_id: str | None = default_list_id or None
        client: TrelloClient | None = None

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
                selected_list_id = (
                    st.text_input("Default list ID", value=default_list_id) or None
                )
        else:
            st.info("Enter API key, token, and board ID to load lists.")
            selected_list_id = (
                st.text_input("Default list ID", value=default_list_id) or None
            )

        delay = st.slider("Delay between creates (seconds)", 0.0, 2.0, 0.25, 0.05)

    return api_key, token, board_id, list_options, selected_list_id, client, delay
