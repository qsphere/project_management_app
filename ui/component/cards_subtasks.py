"""Subtasks (Trello check items) editor for the Cards edit dialog."""

from __future__ import annotations

from typing import Any

import streamlit as st

from clients import TrelloClient
from functions.subtasks import DEFAULT_CHECKLIST_NAME, checklists_to_subtask_groups
from services import (
    create_check_item,
    create_checklist,
    delete_check_item,
    delete_checklist,
    load_card_checklists,
    update_check_item,
)


def _load_groups(client: TrelloClient, card_id: str) -> list[dict[str, Any]]:
    try:
        return checklists_to_subtask_groups(load_card_checklists(client, card_id))
    except Exception as exc:
        st.error(f"Could not load subtasks: {exc}")
        return []


def _toggle_item(
    client: TrelloClient,
    card_id: str,
    item_id: str,
    *,
    complete: bool,
) -> None:
    state = "complete" if complete else "incomplete"
    try:
        update_check_item(client, card_id, item_id, state=state)
        st.rerun()
    except Exception as exc:
        st.error(f"Could not update subtask: {exc}")


def _add_item(
    client: TrelloClient, checklist_id: str, name: str, *, key: str
) -> None:
    text = (name or "").strip()
    if not text:
        st.warning("Subtask name is required.")
        return
    try:
        create_check_item(client, checklist_id, text, checked=False)
        st.session_state[key] = ""
        st.rerun()
    except Exception as exc:
        st.error(f"Could not add subtask: {exc}")


def _delete_item(
    client: TrelloClient, checklist_id: str, item_id: str
) -> None:
    try:
        delete_check_item(client, checklist_id, item_id)
        st.rerun()
    except Exception as exc:
        st.error(f"Could not delete subtask: {exc}")


def _add_group(client: TrelloClient, card_id: str, name: str, *, key: str) -> None:
    text = (name or "").strip() or DEFAULT_CHECKLIST_NAME
    try:
        create_checklist(client, card_id, name=text)
        st.session_state[key] = ""
        st.rerun()
    except Exception as exc:
        st.error(f"Could not add subtask group: {exc}")


def _delete_group(client: TrelloClient, checklist_id: str) -> None:
    try:
        delete_checklist(client, checklist_id)
        st.rerun()
    except Exception as exc:
        st.error(f"Could not delete subtask group: {exc}")


def render_card_subtasks(client: TrelloClient, card_id: str) -> None:
    """Render subtask groups for one card inside the edit dialog."""
    st.subheader("Subtasks")
    st.caption("Trello check items — each item is a subtask.")
    groups = _load_groups(client, card_id)

    if not groups:
        st.caption("No subtasks yet.")

    for group in groups:
        group_id = group["id"]
        with st.container(border=True):
            header_l, header_r = st.columns([4, 1])
            with header_l:
                st.markdown(f"**{group['name']}**")
            with header_r:
                if st.button(
                    "Delete group",
                    key=f"sub_del_group_{group_id}",
                    width="stretch",
                    type="secondary",
                ):
                    _delete_group(client, group_id)

            for item in group["items"]:
                item_id = item["id"]
                row_l, row_r = st.columns([5, 1])
                with row_l:
                    checked = st.checkbox(
                        item["name"] or "(unnamed)",
                        value=item["complete"],
                        key=f"sub_item_{item_id}",
                    )
                    if checked != item["complete"]:
                        _toggle_item(
                            client, card_id, item_id, complete=checked
                        )
                with row_r:
                    if st.button(
                        ":material/delete:",
                        key=f"sub_del_item_{item_id}",
                        width="stretch",
                        help="Delete subtask",
                    ):
                        _delete_item(client, group_id, item_id)

            add_key = f"sub_add_item_{group_id}"
            new_name = st.text_input(
                "Add subtask",
                key=add_key,
                placeholder="New subtask name",
                label_visibility="collapsed",
            )
            if st.button(
                "Add subtask",
                key=f"sub_add_btn_{group_id}",
                width="stretch",
            ):
                _add_item(client, group_id, new_name, key=add_key)

    group_key = f"sub_new_group_{card_id}"
    new_group = st.text_input(
        "New group name",
        key=group_key,
        placeholder=DEFAULT_CHECKLIST_NAME,
    )
    if st.button(
        "Add subtask group",
        key=f"sub_add_group_btn_{card_id}",
        width="stretch",
        icon=":material/playlist_add:",
    ):
        _add_group(client, card_id, new_group, key=group_key)


__all__ = ["render_card_subtasks"]
