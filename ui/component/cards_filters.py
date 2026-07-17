from __future__ import annotations

from datetime import date

import streamlit as st


def render_cards_filters(
    *,
    list_filter_options: list[str],
    default_list_index: int,
    list_options: dict[str, str],
    all_lists_label: str,
    label_name_to_id: dict[str, str],
    member_name_to_id: dict[str, str],
) -> dict:
    with st.container(border=True):
        st.subheader("Filters")
        chosen_list = st.selectbox(
            "List",
            list_filter_options,
            index=default_list_index,
            key="cards_page_list",
        )
        filter_list_id = (
            None if chosen_list == all_lists_label else list_options[chosen_list]
        )

        label_options = sorted(label_name_to_id.keys())
        member_options = sorted(member_name_to_id.keys())
        label_col, assignee_col = st.columns(2)
        with label_col:
            selected_label_names = (
                st.multiselect(
                    "Labels",
                    options=label_options,
                    key="cards_filter_labels",
                    placeholder="Choose options",
                )
                if label_options
                else []
            )
        with assignee_col:
            selected_member_names = (
                st.multiselect(
                    "Assignees",
                    options=member_options,
                    key="cards_filter_assignees",
                    placeholder="Choose options",
                )
                if member_options
                else []
            )

        check_cols = st.columns([1.35, 1.25, 1.1, 1.1, 1.6])
        with check_cols[0]:
            no_labels_only = st.checkbox(
                "Only cards with no labels",
                key="cards_filter_no_labels",
            )
        with check_cols[1]:
            unassigned_only = st.checkbox(
                "Only unassigned cards",
                key="cards_filter_unassigned",
            )
        with check_cols[2]:
            use_due_from = st.checkbox("Due from", key="cards_filter_use_due_from")
            due_from: date | None = None
            if use_due_from:
                due_from = st.date_input(
                    "Due from date",
                    key="cards_filter_due_from",
                    format="MM/DD/YYYY",
                    label_visibility="collapsed",
                )
        with check_cols[3]:
            use_due_to = st.checkbox("Due to", key="cards_filter_use_due_to")
            due_to: date | None = None
            if use_due_to:
                due_to = st.date_input(
                    "Due to date",
                    key="cards_filter_due_to",
                    format="MM/DD/YYYY",
                    label_visibility="collapsed",
                )
        with check_cols[4]:
            include_no_due = st.checkbox(
                "Include cards with no due date",
                value=True,
                key="cards_filter_include_no_due",
                help="When a due range is set, turn this off to exclude undated cards.",
            )

    return {
        "filter_list_id": filter_list_id,
        "selected_label_names": list(selected_label_names),
        "selected_member_names": list(selected_member_names),
        "no_labels_only": no_labels_only,
        "unassigned_only": unassigned_only,
        "use_due_from": use_due_from,
        "due_from": due_from,
        "use_due_to": use_due_to,
        "due_to": due_to,
        "include_no_due": include_no_due,
    }
