from __future__ import annotations

from datetime import datetime

import streamlit as st

from clients import TrelloClient
from constants.taxonomy import DIM_INITIATIVE, ROLLUP_DIMENSIONS
from functions.charts import burndown_chart, donut_chart, status_legend_html
from services import load_initiative_dashboard
from services.taxonomy_io import load_taxonomy_config
from ui.component.auth import current_user
from ui.component.color_selector import inject_dashboard_css
from ui.component.dashboard_filters import render_dashboard_filters
from ui.component.dashboard_tasks import render_visible_tasks
from ui.component.initiative_card import render_initiative_card


def _plural_title(name: str) -> str:
    return name if name.endswith("s") else f"{name}s"


def _section_title(*, group_key: str | None, dimensions: list) -> str:
    if group_key:
        for row in dimensions:
            if row.get("dimension_key") == group_key:
                return _plural_title(str(row.get("name") or group_key))
        return _plural_title(group_key.replace("_", " ").title())
    return "Initiatives"


def render_dashboard_page(client: TrelloClient) -> None:
    inject_dashboard_css()

    user = current_user()
    taxonomy = load_taxonomy_config(user["id"] if user else None)
    lists = client.open_lists()
    labels = client.board_labels()
    board_name = getattr(client, "board_name", None) or client.board_id

    head_l, head_r = st.columns([5, 1])
    with head_l:
        st.markdown("## Dashboard")
        kicker_slot = st.empty()
    with head_r:
        asof_slot = st.empty()

    filters = render_dashboard_filters(
        taxonomy=taxonomy,
        lists=lists,
        labels=labels,
        board_name=str(board_name) if board_name else None,
    )
    if filters is None:
        return

    mappings = filters["mappings"]
    unmapped_policy = taxonomy.get("unmapped_policy") or "show"
    group_key = filters["group_dimension_key"] or DIM_INITIATIVE

    try:
        data = load_initiative_dashboard(
            client,
            lifecycle_filter=filters["lifecycle_filter"],
            group_dimension_key=group_key,
            taxonomy_mappings=mappings or None,
            taxonomy_filters=filters["taxonomy_filters"],
            unmapped_policy=unmapped_policy,
            board_name=str(board_name) if board_name else None,
        )
    except Exception as exc:
        st.error(f"Could not load dashboard data: {exc}")
        return

    as_of_dt = datetime.strptime(data["as_of"], "%Y-%m-%d")
    as_of = as_of_dt.strftime("%b %d").replace(" 0", " ")
    section = _section_title(
        group_key=data.get("group_dimension_key") or group_key,
        dimensions=filters["dimensions"],
    )

    kicker_slot.markdown(
        f'<p class="dash-kicker">Synced from Trello · grouped by '
        f"{section.lower()} · cards = tasks · pies = lifecycle</p>",
        unsafe_allow_html=True,
    )
    asof_slot.markdown(
        f'<div style="text-align:right;padding-top:0.6rem;">'
        f'<span class="dash-asof">As of {as_of}</span></div>',
        unsafe_allow_html=True,
    )

    if data["total_tasks"] == 0 and not data["initiatives"]:
        st.info("No cards match the current filters.")
        return

    top_left, top_right = st.columns(2, gap="large")
    with top_left:
        with st.container(border=True):
            open_n = data["open_tasks"]
            total_n = data["total_tasks"]
            n_init = len(data["initiatives"])
            st.markdown(
                f'<p class="dash-card-title">Overall Burndown</p>'
                f'<p class="dash-card-sub">{open_n} open of {total_n} visible '
                f"tasks across {n_init} {section.lower()}.</p>",
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
                f'<p class="dash-card-title">Tasks by lifecycle</p>'
                f'<p class="dash-card-sub">{data["total_tasks"]} visible tasks · '
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

    render_visible_tasks(
        data.get("visible_tasks") or [],
        group_dimension_key=data.get("group_dimension_key") or group_key,
        dimensions=filters["dimensions"],
    )

    if not data["initiatives"]:
        st.info(
            f"No {section.lower()} matched on this board. "
            f"Map dimensions under Settings → Configuration."
        )
        return

    st.markdown(f"### {section}")
    rollup_note = ""
    gk = data.get("group_dimension_key") or group_key
    if gk in ROLLUP_DIMENSIONS:
        rollup_note = (
            " Completion includes CLOSED and ARCHIVED even when ARCHIVED is "
            "hidden from the visible task list."
        )
    unit = section[:-1] if section.endswith("s") else section
    st.caption(
        f"Each card is a {unit.lower()} value. Charts break tasks down by "
        f"lifecycle.{rollup_note}"
    )
    initiatives = data["initiatives"]
    for row_start in range(0, len(initiatives), 3):
        cols = st.columns(3, gap="large")
        for col, initiative in zip(cols, initiatives[row_start : row_start + 3]):
            with col:
                render_initiative_card(initiative)
