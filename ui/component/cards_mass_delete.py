from __future__ import annotations

import streamlit as st

from services import delete_cards
from clients import TrelloClient


def confirm_bulk_delete(
    client: TrelloClient, selected_bulk: list[dict], *, delay: float
) -> None:
    count = len(selected_bulk)

    @st.dialog(f"Delete {count} card(s)?")
    def _confirm() -> None:
        st.write(
            f"This will permanently delete {count} selected card(s). "
            "This action cannot be undone."
        )
        cancel_col, delete_col = st.columns(2)
        if cancel_col.button("Cancel", width="stretch", key="cards_bulk_cancel"):
            st.rerun()
        if delete_col.button(
            "Delete",
            type="primary",
            width="stretch",
            key="cards_bulk_confirm_delete",
        ):
            try:
                progress = st.progress(0, text=f"Deleting… 0/{count}")

                def _on_progress(done: int, total: int, message: str) -> None:
                    fraction = done / total if total else 1.0
                    progress.progress(min(fraction, 1.0), text=message)

                deleted = delete_cards(
                    client,
                    selected_bulk,
                    delay=delay,
                    on_progress=_on_progress,
                )
                st.success(f"Deleted {deleted} card(s).")
                st.session_state["cards_selected_ids"] = []
                st.session_state.pop("cards_manage_table", None)
                st.session_state.pop("cards_manage_table_v2", None)
                st.session_state.pop("cards_manage_table_v3", None)
                st.session_state.pop("cards_manage_table_v4", None)
                st.session_state.pop("edit_card_sync_id", None)
                st.rerun()
            except Exception as exc:
                st.error(f"Could not delete cards: {exc}")

    _confirm()
