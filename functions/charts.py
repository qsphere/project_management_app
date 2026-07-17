from __future__ import annotations

import altair as alt
import pandas as pd


def burndown_chart(
    points: list[dict],
    *,
    height: int = 260,
    accent: str = "#3B82F6",
    show_today: bool = True,
) -> alt.Chart | None:
    if not points:
        return None
    df = pd.DataFrame(points)
    df["date"] = pd.to_datetime(df["date"])
    remaining = (
        alt.Chart(df)
        .mark_line(strokeWidth=2.5, color=accent)
        .encode(
            x=alt.X("date:T", title=None, axis=alt.Axis(format="%b %d", labelAngle=0)),
            y=alt.Y("remaining:Q", title=None),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("remaining:Q", title="Remaining"),
                alt.Tooltip("ideal:Q", title="Ideal"),
            ],
        )
    )
    ideal = (
        alt.Chart(df)
        .mark_line(strokeDash=[5, 5], strokeWidth=1.5, color="#9CA3AF")
        .encode(x="date:T", y="ideal:Q")
    )
    layers: list[alt.Chart] = [ideal, remaining]
    if show_today:
        today_df = df[df["is_today"] == True]  # noqa: E712
        if not today_df.empty:
            layers.append(
                alt.Chart(today_df)
                .mark_rule(strokeDash=[4, 4], color="#EF4444", strokeWidth=1.5)
                .encode(x="date:T")
            )
    return alt.layer(*layers).properties(height=height).configure_view(strokeWidth=0)


def donut_chart(
    breakdown: list[dict],
    *,
    height: int = 220,
    center_label: str | None = None,
) -> alt.Chart | None:
    rows = [row for row in breakdown if row.get("count", 0) > 0]
    if not rows:
        rows = [{"status": "Empty", "count": 1, "pct": 100, "color": "#E5E7EB"}]
    df = pd.DataFrame(rows)
    color_scale = alt.Scale(
        domain=[row["status"] for row in rows],
        range=[row["color"] for row in rows],
    )
    donut = (
        alt.Chart(df)
        .mark_arc(
            innerRadius=58 if height >= 200 else 42,
            outerRadius=90 if height >= 200 else 68,
        )
        .encode(
            theta=alt.Theta("count:Q", stack=True),
            color=alt.Color("status:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("status:N", title="Status"),
                alt.Tooltip("count:Q", title="Tasks"),
                alt.Tooltip("pct:Q", title="%"),
            ],
        )
    )
    if center_label:
        text = (
            alt.Chart(pd.DataFrame({"label": [center_label]}))
            .mark_text(
                fontSize=22 if height >= 200 else 16,
                fontWeight="bold",
                color="#111827",
            )
            .encode(text="label:N")
        )
        sub = (
            alt.Chart(pd.DataFrame({"label": ["complete"]}))
            .mark_text(fontSize=11, color="#6B7280", dy=16)
            .encode(text="label:N")
        )
        chart = alt.layer(donut, text, sub)
    else:
        chart = donut
    return chart.properties(height=height, width=220).configure_view(strokeWidth=0)


def status_legend_html(breakdown: list[dict]) -> str:
    parts = []
    for row in breakdown:
        pct = row.get("pct", 0)
        count = row.get("count", 0)
        parts.append(
            '<div class="dash-status-row">'
            f'<span class="dash-status-left">'
            f'<span class="dash-dot" style="background:{row["color"]}"></span>'
            f'{row["status"]}</span>'
            f'<span class="dash-status-pct">{pct:.0f}%'
            f'<span style="color:#9ca3af;font-weight:500;margin-left:0.35rem;">'
            f"({count})</span></span>"
            "</div>"
        )
    return "".join(parts) or '<p class="dash-card-sub">No list data.</p>'
