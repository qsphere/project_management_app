from __future__ import annotations

from datetime import datetime

import streamlit as st

from constants.entity_config import MAPS_TO_LABELS
from constants.status import LIFECYCLE_ORDER
from services import load_initiative_dashboard
from services.entity_config import dashboard_entity_maps
from ui.component.auth import current_user
from ui.component.color_selector import inject_dashboard_css
from ui.component.initiative_card import render_initiative_card
from clients import TrelloClient
from functions.charts import burndown_chart, donut_chart, status_legend_html


def _trello_noun(maps_to: str) -> str:
    return "label" if maps_to == MAPS_TO_LABELS else "list"


def _plural_title(name: str) -> str:
    return name if name.endswith("s") else f"{name}s"


def render_dashboard_page(client: TrelloClient) -> None:
    inject_dashboard_css()

    user = current_user()
    entity_maps = dashboard_entity_maps(user["id"] if user else None)
    init_cfg = entity_maps["initiative"]
    status_cfg = entity_maps["status"]
    init_name = init_cfg["name"]
    status_name = status_cfg["name"]
    init_maps = init_cfg["maps_to"]

    selected = st.multiselect(
        "Lifecycle status",
        options=list(LIFECYCLE_ORDER),
        default=list(LIFECYCLE_ORDER),
        help="Filter tasks by derived lifecycleStatus (recomputed on each sync).",
        key="dashboard_lifecycle_filter",
    )
    if not selected:
        st.info("Select at least one lifecycle status to show tasks.")
        return

    try:
        data = load_initiative_dashboard(
            client,
            initiative_maps_to=init_maps,
            lifecycle_filter=set(selected),
        )
    except Exception as exc:
        st.error(f"Could not load dashboard data: {exc}")
        return

    as_of_dt = datetime.strptime(data["as_of"], "%Y-%m-%d")
    as_of = as_of_dt.strftime("%b %d").replace(" 0", " ")
    init_noun = _trello_noun(init_maps)

    head_l, head_r = st.columns([5, 1])
    with head_l:
        st.markdown("## Initiative Dashboard")
        st.markdown(
            f'<p class="dash-kicker">Synced from Trello · '
            f"{init_noun}s = {init_name.lower()}s, cards = tasks · "
            f"pie slices = lifecycle ({status_name.lower()})</p>",
            unsafe_allow_html=True,
        )
    with head_r:
        st.markdown(
            f'<div style="text-align:right;padding-top:0.6rem;">'
            f'<span class="dash-asof">As of {as_of}</span></div>',
            unsafe_allow_html=True,
        )

    if data["total_tasks"] == 0:
        if set(selected) != set(LIFECYCLE_ORDER):
            st.info("No tasks match the selected lifecycle statuses.")
        else:
            st.info(
                "No cards on this board yet. Import tasks or add cards in Trello."
            )
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
                f"across {n_init} {_plural_title(init_name).lower()}.</p>",
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
                f'<p class="dash-card-title">Tasks by {status_name}</p>'
                f'<p class="dash-card-sub">All {data["total_tasks"]} tasks · '
                f"OPEN / CLOSED / ARCHIVED from card flags.</p>",
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

    section = _plural_title(init_name)
    if not data["initiatives"]:
        st.info(
            f"No {init_noun}-based {section.lower()} on this board yet. "
            f"Map {init_name} under Settings → Configuration, then apply "
            f"named {init_noun}s to cards."
        )
        return

    st.markdown(f"### {section}")
    st.caption(
        f"Each card is a Trello {init_noun}. Charts break that "
        f"{init_name.lower()}'s tasks down by lifecycle {status_name.lower()}."
    )
    initiatives = data["initiatives"]
    for row_start in range(0, len(initiatives), 3):
        cols = st.columns(3, gap="large")
        for col, initiative in zip(cols, initiatives[row_start : row_start + 3]):
            with col:
                render_initiative_card(initiative)
