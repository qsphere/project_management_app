from __future__ import annotations

import streamlit as st

from ui.component.cards_edit import open_card_delete_dialog, open_card_edit_dialog
from ui.component.cards_filters import render_cards_filters
from ui.component.cards_table import render_cards_table
from clients import TrelloClient
from functions.cards import filter_cards
from services import load_cards_manage


def render_manage_tab(
    client: TrelloClient,
    *,
    list_options: dict[str, str],
    default_list_id: str | None,
    delay: float = 0.25,
) -> None:
    if not list_options:
        st.warning("No open lists found on this board.")
        return

    list_names = list(list_options.keys())
    list_id_to_name = {list_id: name for name, list_id in list_options.items()}
    all_lists_label = "All lists"
    list_filter_options = [all_lists_label, *list_names]
    default_list_index = 0
    if default_list_id:
        for i, name in enumerate(list_names):
            if list_options[name] == default_list_id:
                default_list_index = i + 1
                break

    try:
        cards, board_labels, board_members = load_cards_manage(client)
    except Exception as exc:
        st.error(f"Could not load cards: {exc}")
        return

    label_names = {
        item["id"]: item["name"] or "(unnamed)" for item in board_labels
    }
    member_names = {
        item["id"]: item.get("fullName") or item.get("username") or item["id"]
        for item in board_members
    }
    label_name_to_id = {name: lid for lid, name in label_names.items()}
    member_name_to_id = {name: mid for mid, name in member_names.items()}

    filters = render_cards_filters(
        list_filter_options=list_filter_options,
        default_list_index=default_list_index,
        list_options=list_options,
        all_lists_label=all_lists_label,
        label_name_to_id=label_name_to_id,
        member_name_to_id=member_name_to_id,
    )

    filtered = filter_cards(
        cards,
        list_id=filters["filter_list_id"],
        label_ids=(
            None
            if filters["no_labels_only"]
            else [label_name_to_id[name] for name in filters["selected_label_names"]]
        ),
        member_ids=(
            None
            if filters["unassigned_only"]
            else [member_name_to_id[name] for name in filters["selected_member_names"]]
        ),
        due_from=filters["due_from"],
        due_to=filters["due_to"],
        include_no_due=filters["include_no_due"],
        unassigned_only=filters["unassigned_only"],
        no_labels_only=filters["no_labels_only"],
    )

    if not cards:
        st.info("No open cards on this board.")
        return

    due_from = filters["due_from"]
    due_to = filters["due_to"]
    # Only filter controls — not the card id set — so a board reload cannot
    # wipe row selection (and reset Delete selected to 0) on every rerun.
    filter_sig = (
        filters["filter_list_id"],
        tuple(filters["selected_label_names"]),
        tuple(filters["selected_member_names"]),
        filters["no_labels_only"],
        filters["unassigned_only"],
        filters["use_due_from"],
        due_from.isoformat() if due_from else None,
        filters["use_due_to"],
        due_to.isoformat() if due_to else None,
        filters["include_no_due"],
    )

    render_cards_table(
        client=client,
        cards=cards,
        filtered=filtered,
        list_id_to_name=list_id_to_name,
        label_names=label_names,
        member_names=member_names,
        filter_sig=filter_sig,
        delay=delay,
    )

    open_card_edit_dialog(
        client,
        filtered=filtered,
        list_names=list_names,
        list_options=list_options,
        list_id_to_name=list_id_to_name,
    )
    if not st.session_state.get("cards_edit_id"):
        open_card_delete_dialog(client, filtered)
