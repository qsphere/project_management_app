from __future__ import annotations

import pandas as pd
import streamlit as st

from services import create_label, delete_label, load_board_labels, update_label
from ui.component.color_selector import render_color_selector
from constants.colors import LABEL_COLORS
from clients import TrelloClient


def render_label_crud(client: TrelloClient) -> None:
    st.divider()
    st.subheader("Board labels")
    st.caption(
        "Spreadsheet Labels values are matched by name (case-insensitive). "
        "Missing names are created automatically on import."
    )

    try:
        labels = load_board_labels(client)
    except Exception as exc:
        st.error(f"Could not load labels: {exc}")
        return

    if not labels:
        st.info("This board has no labels yet.")
    else:
        rows = []
        for item in labels:
            color = item.get("color") or "(none)"
            display_name = item["name"] or "(unnamed)"
            rows.append(
                {
                    "Name": display_name,
                    "Color": color,
                    "Uses": item.get("uses", 0),
                    "ID": item["id"],
                }
            )
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    st.divider()
    st.subheader("Create label")
    new_name = st.text_input("Name", placeholder="e.g. Bug", key="create_label_name")
    create_color = render_color_selector("create_label_color", default="red")
    if st.button("Create label", type="primary", key="create_label_btn"):
        name = (new_name or "").strip()
        if not name:
            st.error("Name is required.")
        else:
            try:
                color = None if create_color == "(none)" else create_color
                created = create_label(client, name, color)
                st.success(
                    f"Created label {created.get('name')!r} "
                    f"({created.get('color') or 'no color'})."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Could not create label: {exc}")

    if not labels:
        return

    st.divider()
    st.subheader("Edit or delete label")
    label_choices = {
        f"{(item['name'] or '(unnamed)')} · {item.get('color') or 'none'}": item
        for item in labels
    }
    selected_key = st.selectbox("Label", list(label_choices.keys()))
    selected = label_choices[selected_key]

    # Keep edit color in sync when the chosen label changes.
    edit_sync_key = "edit_label_sync_id"
    current_color = selected.get("color") or "(none)"
    if st.session_state.get(edit_sync_key) != selected["id"]:
        valid = current_color in {*(LABEL_COLORS), "(none)"}
        st.session_state["edit_label_color"] = current_color if valid else "red"
        st.session_state[edit_sync_key] = selected["id"]

    edit_name = st.text_input("Name", value=selected["name"], key="edit_label_name")
    edit_color = render_color_selector(
        "edit_label_color",
        default=current_color if current_color in {*(LABEL_COLORS), "(none)"} else "red",
    )

    col_save, col_delete = st.columns(2)
    if col_save.button("Save changes", width="stretch", key="save_label_btn"):
        name = (edit_name or "").strip()
        color = "" if edit_color == "(none)" else edit_color
        try:
            update_label(client, selected["id"], name=name, color=color)
            st.success("Label updated.")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not update label: {exc}")

    if col_delete.button("Delete label", width="stretch", key="delete_label_btn"):
        try:
            delete_label(client, selected["id"])
            st.success("Label deleted.")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not delete label: {exc}")
