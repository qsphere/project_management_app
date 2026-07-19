from __future__ import annotations

import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from ui.component.cards_mass_delete import confirm_bulk_delete
from functions.dates import display_card_date
from clients import TrelloClient
from services import excel_cards_export_bytes

# Bust stale dataframe state when action columns change shape.
_TABLE_KEY = "cards_manage_table_v4"
_LEGACY_TABLE_KEYS = (
    "cards_manage_table",
    "cards_manage_table_v2",
    "cards_manage_table_v3",
)
_EXPORT_MIME = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

_EDIT_ACTION = ":material/edit: Edit"
_VIEW_ACTION = ":material/open_in_new: Open in Trello"
_DELETE_ACTION = ":material/delete: Delete"


def _clear_table_selection() -> None:
    st.session_state["cards_selected_ids"] = []
    st.session_state[_TABLE_KEY] = {"selection": {"rows": [], "columns": []}}


def _drop_legacy_table_state() -> None:
    for key in _LEGACY_TABLE_KEYS:
        st.session_state.pop(key, None)


def _render_toolbar(
    *,
    selected_count: int,
    disabled: bool,
    export_bytes: bytes | None = None,
) -> bool:
    clear_col, export_col, delete_col = st.columns(3)
    with clear_col:
        if st.button(
            "Clear selection",
            width="stretch",
            key="cards_bulk_clear",
            disabled=disabled,
        ):
            _clear_table_selection()
            st.rerun()
    with export_col:
        st.download_button(
            f"Export selection ({selected_count})",
            data=export_bytes or b"",
            file_name="trello_cards_export.xlsx",
            mime=_EXPORT_MIME,
            width="stretch",
            key="cards_bulk_export",
            icon=":material/download:",
            disabled=disabled or selected_count == 0 or not export_bytes,
        )
    with delete_col:
        return st.button(
            f"Delete selected ({selected_count})",
            width="stretch",
            key="cards_bulk_delete_btn",
            type="primary",
            disabled=disabled or selected_count == 0,
        )


def _row_actions(card: dict) -> list[str]:
    actions = [_EDIT_ACTION]
    if card.get("shortUrl"):
        actions.append(_VIEW_ACTION)
    actions.append(_DELETE_ACTION)
    return actions


def _on_action_click(ordered: list[dict]) -> None:
    click = st.session_state.get("cards_action_click")
    if not click:
        return
    row = int(click["row"])
    if not (0 <= row < len(ordered)):
        return
    card = ordered[row]
    label = click["label"]
    if label == _EDIT_ACTION:
        st.session_state["cards_edit_id"] = card["id"]
    elif label == _VIEW_ACTION:
        st.session_state["cards_open_url"] = card.get("shortUrl") or ""
    elif label == _DELETE_ACTION:
        st.session_state["cards_delete_id"] = card["id"]


def _open_trello_url_if_requested() -> None:
    url = st.session_state.pop("cards_open_url", None)
    if url:
        components.html(
            f"<script>window.open({json.dumps(url)}, '_blank');</script>",
            height=0,
        )


def render_cards_table(
    *,
    client: TrelloClient,
    cards: list[dict],
    filtered: list[dict],
    list_id_to_name: dict[str, str],
    label_names: dict[str, str],
    member_names: dict[str, str],
    filter_sig: tuple,
    delay: float,
) -> list[dict]:
    if "cards_selected_ids" not in st.session_state:
        st.session_state["cards_selected_ids"] = []
    _drop_legacy_table_state()

    if st.session_state.get("cards_table_sig") != filter_sig:
        st.session_state["cards_table_sig"] = filter_sig
        _clear_table_selection()

    if not filtered:
        summary_l, summary_r = st.columns([2, 1])
        with summary_l:
            st.caption(f"0 of {len(cards)} card(s) shown")
        with summary_r:
            _render_toolbar(selected_count=0, disabled=True)
        st.info("No cards match the current filters.")
        return []

    # Stable order so row indices stay valid across API reorderings.
    ordered = sorted(filtered, key=lambda card: card["id"])
    rows = []
    for card in ordered:
        labels = ", ".join(
            label_names.get(lid, lid) for lid in card.get("idLabels") or []
        )
        members = ", ".join(
            member_names.get(mid, mid) for mid in card.get("idMembers") or []
        )
        rows.append(
            {
                "NAME": card["name"],
                "LIST": list_id_to_name.get(card.get("idList") or "", "—"),
                "DESCRIPTION": (card.get("desc") or "")[:80],
                "DUE": display_card_date(card.get("due")),
                "LABELS": labels or "—",
                "ASSIGNEE": members or "—",
                "ACTIONS": _row_actions(card),
                "_id": card["id"],
            }
        )
    df = pd.DataFrame(rows)

    summary_l, summary_r = st.columns([2, 1])
    with summary_l:
        st.caption(f"{len(filtered)} of {len(cards)} card(s) shown")
    with summary_r:
        # Placeholder so actions stay above the table but read selection after it.
        toolbar = st.empty()

    event = st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
        column_config={
            "NAME": st.column_config.TextColumn("NAME", width="large"),
            "LIST": st.column_config.TextColumn("LIST", width="medium"),
            "DESCRIPTION": st.column_config.TextColumn(
                "DESCRIPTION", width="large"
            ),
            "DUE": st.column_config.TextColumn("DUE", width="small"),
            "LABELS": st.column_config.TextColumn("LABELS", width="small"),
            "ASSIGNEE": st.column_config.TextColumn("ASSIGNEE", width="medium"),
            "ACTIONS": st.column_config.ButtonColumn(
                "ACTIONS",
                width="small",
                type="tertiary",
                help="Edit, open in Trello, or delete",
                on_click=_on_action_click,
                args=(ordered,),
                key="cards_action_click",
            ),
            "_id": None,
        },
        key=_TABLE_KEY,
    )
    _open_trello_url_if_requested()

    selected_rows = [int(i) for i in event.selection.rows if 0 <= int(i) < len(df)]
    st.session_state["cards_selected_ids"] = [
        df.iloc[i]["_id"] for i in selected_rows
    ]
    selected_count = len(selected_rows)
    card_by_id = {card["id"]: card for card in ordered}
    selected_bulk = [
        card_by_id[card_id]
        for card_id in st.session_state["cards_selected_ids"]
        if card_id in card_by_id
    ]

    with toolbar.container():
        export_bytes = (
            excel_cards_export_bytes(
                selected_bulk,
                list_id_to_name=list_id_to_name,
                label_names=label_names,
                member_names=member_names,
            )
            if selected_bulk
            else None
        )
        delete_clicked = _render_toolbar(
            selected_count=selected_count,
            disabled=False,
            export_bytes=export_bytes,
        )

    if delete_clicked and selected_bulk:
        confirm_bulk_delete(client, selected_bulk, delay=delay)

    return selected_bulk
