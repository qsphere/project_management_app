from __future__ import annotations

import pandas as pd
import streamlit as st

from services import label_dashboard_rows, load_label_dashboard
from constants.colors import COLOR_SWATCH
from clients import TrelloClient


def render_label_overview(client: TrelloClient) -> None:
    st.subheader("Label dashboard")
    st.caption(
        "Open cards on this board, grouped by label. "
        "% of label is that label's cards in each list; "
        "% of list is how much of that list carries the label."
    )

    try:
        labels, cards, lists = load_label_dashboard(client)
    except Exception as exc:
        st.error(f"Could not load dashboard data: {exc}")
        return

    if not labels:
        st.info("This board has no labels yet.")
        return

    dashboard = label_dashboard_rows(labels, cards, lists)

    overview_rows = []
    for item in dashboard:
        color = item.get("color") or "(none)"
        top_list = item["lists"][0]["list_name"] if item["lists"] else "—"
        overview_rows.append(
            {
                "Label": item["name"] or "(unnamed)",
                "Color": color,
                "Cards": item["total"],
                "Lists": len(item["lists"]),
                "Top list": top_list,
            }
        )

    overview_df = pd.DataFrame(overview_rows)
    display_cols = ["Label", "Color", "Cards", "Lists", "Top list"]
    st.dataframe(
        overview_df[display_cols],
        width="stretch",
        hide_index=True,
    )

    labeled_cards = sum(item["total"] for item in dashboard)
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Labels", len(dashboard))
    col_b.metric("Open cards", len(cards))
    col_c.metric("Label applications", labeled_cards)

    choices = {
        f"{(item['name'] or '(unnamed)')} · {item['total']} card(s)": item
        for item in dashboard
    }
    selected_key = st.selectbox(
        "Label breakdown",
        list(choices.keys()),
        key="label_dashboard_select",
    )
    selected = choices[selected_key]

    color = selected.get("color") or "(none)"
    swatch = COLOR_SWATCH.get(color, "#DFE1E6")
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:4px 0 12px;">'
        f'<div style="background:{swatch};width:28px;height:28px;border-radius:6px;'
        f'border:1px solid #dfe1e6;"></div>'
        f"<div><strong>{selected['name'] or '(unnamed)'}</strong> · "
        f"{selected['total']} card(s)</div></div>",
        unsafe_allow_html=True,
    )

    if selected["total"] == 0:
        st.info("No open cards currently use this label.")
        return

    breakdown_rows = [
        {
            "List": entry["list_name"],
            "Cards": entry["count"],
            "% of label": entry["pct_of_label"],
            "% of list": entry["pct_of_list"],
        }
        for entry in selected["lists"]
    ]
    breakdown_df = pd.DataFrame(breakdown_rows)
    st.dataframe(breakdown_df, width="stretch", hide_index=True)

    chart_df = breakdown_df.set_index("List")[["% of label"]]
    st.bar_chart(chart_df, horizontal=True)
