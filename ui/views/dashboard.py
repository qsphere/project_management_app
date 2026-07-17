from __future__ import annotations

from datetime import datetime

import streamlit as st

from services import load_initiative_dashboard
from ui.component.color_selector import inject_dashboard_css
from ui.component.initiative_card import render_initiative_card
from clients import TrelloClient
from functions.charts import burndown_chart, donut_chart, status_legend_html


def render_dashboard_page(client: TrelloClient) -> None:
    inject_dashboard_css()

    try:
        data = load_initiative_dashboard(client)
    except Exception as exc:
        st.error(f"Could not load dashboard data: {exc}")
        return

    as_of_dt = datetime.strptime(data["as_of"], "%Y-%m-%d")
    as_of = as_of_dt.strftime("%b %d").replace(" 0", " ")

    head_l, head_r = st.columns([5, 1])
    with head_l:
        st.markdown("## Initiative Dashboard")
        st.markdown(
            '<p class="dash-kicker">Synced from Trello · labels = initiatives, '
            "cards = tasks · pie slices = lists</p>",
            unsafe_allow_html=True,
        )
    with head_r:
        st.markdown(
            f'<div style="text-align:right;padding-top:0.6rem;">'
            f'<span class="dash-asof">As of {as_of}</span></div>',
            unsafe_allow_html=True,
        )

    if data["total_tasks"] == 0:
        st.info("No cards on this board yet. Import tasks or add cards in Trello.")
        return

    top_left, top_right = st.columns(2, gap="large")

    with top_left:
        with st.container(border=True):
            open_n = data["open_tasks"]
            total_n = data["total_tasks"]
            n_init = len(data["initiatives"])
            st.markdown(
                f'<p class="dash-card-title">Overall Burndown</p>'
                f'<p class="dash-card-sub">{open_n} open of {total_n} tasks '
                f"across {n_init} initiative{'s' if n_init != 1 else ''}.</p>",
                unsafe_allow_html=True,
            )
            chart = burndown_chart(
                data["overall_burndown"], height=280, accent="#3B82F6"
            )
            if chart is not None:
                st.altair_chart(chart, width="stretch")
            else:
                st.caption("Not enough date data to plot a burndown.")
            st.caption("Solid = remaining tasks · dashed = ideal pace · red = today")

    with top_right:
        with st.container(border=True):
            st.markdown(
                f'<p class="dash-card-title">Tasks by List</p>'
                f'<p class="dash-card-sub">All {data["total_tasks"]} tasks · '
                "slice labels are Trello list names.</p>",
                unsafe_allow_html=True,
            )
            donut_col, legend_col = st.columns([1.1, 1])
            with donut_col:
                donut = donut_chart(
                    data["status_breakdown"],
                    height=230,
                    center_label=f'{data["complete_pct"]}%',
                )
                if donut is not None:
                    st.altair_chart(donut, width="stretch")
            with legend_col:
                st.markdown(
                    status_legend_html(data["status_breakdown"]),
                    unsafe_allow_html=True,
                )

    if not data["initiatives"]:
        st.info(
            "No labeled cards on this board yet. Apply named labels to cards — "
            "each label becomes an initiative on this dashboard."
        )
        return

    st.markdown("### Initiatives")
    st.caption("Each card is a Trello label. Charts break that label’s tasks down by list.")
    initiatives = data["initiatives"]
    for row_start in range(0, len(initiatives), 3):
        cols = st.columns(3, gap="large")
        for col, initiative in zip(cols, initiatives[row_start : row_start + 3]):
            with col:
                render_initiative_card(initiative)
