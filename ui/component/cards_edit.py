from __future__ import annotations

import streamlit as st

from services import delete_card, update_card
from clients import TrelloClient
from functions.dates import format_date_field, format_due, parse_card_date
from functions.cards import unique_card_choices


def _clear_edit_dialog() -> None:
    st.session_state.pop("cards_edit_id", None)
    st.session_state.pop("cards_edit_opened_for", None)
    st.session_state.pop("edit_card_sync_id", None)


def _sync_edit_fields(selected: dict, list_id_to_name: dict[str, str], list_names: list[str]) -> None:
    selected_list_name = list_id_to_name.get(
        selected.get("idList") or "", list_names[0]
    )
    edit_sync_key = "edit_card_sync_id"
    if st.session_state.get(edit_sync_key) != selected["id"]:
        st.session_state["edit_card_name"] = selected["name"]
        st.session_state["edit_card_desc"] = selected.get("desc") or ""
        st.session_state["edit_card_due_date"] = parse_card_date(selected.get("due"))
        st.session_state["edit_card_start_date"] = parse_card_date(
            selected.get("start")
        )
        st.session_state["edit_card_list"] = selected_list_name
        st.session_state[edit_sync_key] = selected["id"]


def _save_card(
    client: TrelloClient,
    selected: dict,
    *,
    edit_name: str,
    edit_desc: str,
    edit_due,
    edit_start,
    edit_list: str,
    list_options: dict[str, str],
) -> None:
    name = (edit_name or "").strip()
    if not name:
        st.error("Name is required.")
        return
    try:
        due_value = edit_due.isoformat() if edit_due else ""
        start_value = edit_start.isoformat() if edit_start else ""
        if due_value:
            due_value = format_due(due_value) or due_value
        if start_value:
            start_value = (
                format_date_field(start_value, field_name="start date") or start_value
            )
        update_card(
            client,
            selected["id"],
            name=name,
            desc=edit_desc or "",
            due=due_value,
            start=start_value,
            id_list=list_options[edit_list],
        )
        st.success("Card updated.")
        _clear_edit_dialog()
        st.rerun()
    except Exception as exc:
        st.error(f"Could not update card: {exc}")


def _delete_from_edit(client: TrelloClient, selected: dict) -> None:
    try:
        delete_card(client, selected["id"])
        st.success("Card deleted.")
        st.session_state["cards_selected_ids"] = [
            card_id
            for card_id in st.session_state.get("cards_selected_ids", [])
            if card_id != selected["id"]
        ]
        _clear_edit_dialog()
        st.rerun()
    except Exception as exc:
        st.error(f"Could not delete card: {exc}")


def open_card_edit_dialog(
    client: TrelloClient,
    *,
    filtered: list[dict],
    list_names: list[str],
    list_options: dict[str, str],
    list_id_to_name: dict[str, str],
) -> None:
    edit_id = st.session_state.get("cards_edit_id")
    if not edit_id or not filtered:
        return

    card_choices = unique_card_choices(filtered, list_id_to_name)
    labels = list(card_choices.keys())
    initial_label = next(
        (
            label
            for label, card in card_choices.items()
            if card["id"] == edit_id
        ),
        labels[0] if labels else None,
    )
    if initial_label is None:
        _clear_edit_dialog()
        return
    # Re-bind the selectbox when opening edit for a different card.
    if st.session_state.get("cards_edit_opened_for") != edit_id:
        st.session_state["cards_page_card"] = initial_label
        st.session_state["cards_edit_opened_for"] = edit_id
        st.session_state.pop("edit_card_sync_id", None)
    elif st.session_state.get("cards_page_card") not in card_choices:
        st.session_state["cards_page_card"] = initial_label

    @st.dialog("Edit or delete card", width="medium", on_dismiss=_clear_edit_dialog)
    def _dialog() -> None:
        selected_key = st.selectbox("Card", labels, key="cards_page_card")
        selected = card_choices[selected_key]
        _sync_edit_fields(selected, list_id_to_name, list_names)

        edit_name = st.text_input("Name", key="edit_card_name")
        edit_desc = st.text_area("Description", key="edit_card_desc", height=120)
        due_col, start_col = st.columns(2)
        with due_col:
            edit_due = st.date_input(
                "Due date", key="edit_card_due_date", format="MM/DD/YYYY"
            )
        with start_col:
            edit_start = st.date_input(
                "Start date", key="edit_card_start_date", format="MM/DD/YYYY"
            )
        edit_list = st.selectbox("Move to list", list_names, key="edit_card_list")

        if selected.get("shortUrl"):
            st.markdown(
                f"[Open in Trello :material/open_in_new:]({selected['shortUrl']})"
            )

        col_save, col_delete = st.columns(2)
        if col_save.button(
            "Save changes", width="stretch", key="save_card_btn", type="primary"
        ):
            _save_card(
                client,
                selected,
                edit_name=edit_name,
                edit_desc=edit_desc,
                edit_due=edit_due,
                edit_start=edit_start,
                edit_list=edit_list,
                list_options=list_options,
            )
        if col_delete.button(
            "Delete card", width="stretch", key="delete_card_btn", type="secondary"
        ):
            _delete_from_edit(client, selected)

    _dialog()


def open_card_delete_dialog(client: TrelloClient, cards: list[dict]) -> None:
    delete_id = st.session_state.get("cards_delete_id")
    if not delete_id:
        return
    card = next((c for c in cards if c["id"] == delete_id), None)
    if card is None:
        st.session_state.pop("cards_delete_id", None)
        return

    def _clear_delete() -> None:
        st.session_state.pop("cards_delete_id", None)

    @st.dialog("Delete card?", on_dismiss=_clear_delete)
    def _confirm() -> None:
        st.write(
            f'This will permanently delete **{card["name"] or "(unnamed)"}**. '
            "This action cannot be undone."
        )
        cancel_col, delete_col = st.columns(2)
        if cancel_col.button("Cancel", width="stretch", key="cards_single_cancel"):
            _clear_delete()
            st.rerun()
        if delete_col.button(
            "Delete", type="primary", width="stretch", key="cards_single_confirm"
        ):
            try:
                delete_card(client, card["id"])
                st.success("Card deleted.")
                st.session_state["cards_selected_ids"] = [
                    cid
                    for cid in st.session_state.get("cards_selected_ids", [])
                    if cid != card["id"]
                ]
                _clear_delete()
                st.session_state.pop("edit_card_sync_id", None)
                st.rerun()
            except Exception as exc:
                st.error(f"Could not delete card: {exc}")

    _confirm()
