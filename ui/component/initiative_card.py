from __future__ import annotations

import streamlit as st

from constants.colors import COLOR_SWATCH
from functions.charts import burndown_chart, donut_chart, status_legend_html
from functions.dates import format_target


def render_initiative_card(initiative: dict) -> None:
    badge_class = (
        "dash-badge-risk" if initiative["status"] == "At Risk" else "dash-badge-ok"
    )
    accent = (
        "#F59E0B" if initiative["status"] == "At Risk" else "#10B981"
    )
    target = format_target(initiative.get("target_date"))
    label_color = initiative.get("color") or "(none)"
    swatch = COLOR_SWATCH.get(label_color, "#DFE1E6")
    with st.container(border=True):
        title_col, badge_col = st.columns([3, 1.2])
        with title_col:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;">'
                f'<span style="background:{swatch};width:14px;height:14px;'
                f'border-radius:4px;border:1px solid #d1d5db;flex-shrink:0;"></span>'
                f'<p class="dash-card-title">{initiative["name"]}</p>'
                f"</div>",
                unsafe_allow_html=True,
            )
        with badge_col:
            st.markdown(
                f'<div style="text-align:right;padding-top:0.15rem;">'
                f'<span class="dash-badge {badge_class}">{initiative["status"]}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<p class="dash-card-sub">{target} · {initiative["total"]} tasks</p>',
            unsafe_allow_html=True,
        )

        donut_col, legend_col = st.columns([1, 1.15])
        with donut_col:
            donut = donut_chart(
                initiative["status_breakdown"],
                height=170,
                center_label=f'{initiative["complete_pct"]}%',
            )
            if donut is not None:
                st.altair_chart(donut, width="stretch")
        with legend_col:
            st.markdown(
                status_legend_html(initiative["status_breakdown"]),
                unsafe_allow_html=True,
            )

        st.markdown(
            '<p class="dash-mini-label">BURNDOWN TO TARGET</p>',
            unsafe_allow_html=True,
        )
        spark = burndown_chart(
            initiative["burndown"],
            height=110,
            accent=accent,
            show_today=True,
        )
        if spark is not None:
            st.altair_chart(spark, width="stretch")
        else:
            st.caption("No burndown data yet.")
