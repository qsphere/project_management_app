"""Dashboard filter controls: lifecycle, group-by, taxonomy values."""

from __future__ import annotations

from typing import Any

import streamlit as st

from constants.status import LIFECYCLE_DEFAULT_FILTER, LIFECYCLE_ORDER
from constants.taxonomy import DIM_INITIATIVE
from functions.taxonomy import dimension_source_map
from functions.taxonomy_filter import (
    board_values_for_source,
    dimension_keys_with_mappings,
)


def _dim_label(dimensions: list[dict[str, Any]], key: str) -> str:
    for row in dimensions:
        if row.get("dimension_key") == key:
            return str(row.get("name") or key)
    return key.replace("_", " ").title()


def render_dashboard_filters(
    *,
    taxonomy: dict[str, Any],
    lists: list[dict[str, Any]] | None = None,
    labels: list[dict[str, Any]] | None = None,
    board_name: str | None = None,
) -> dict[str, Any] | None:
    """
    Render always-on lifecycle + optional taxonomy filters.

    Returns filter selections, or None when lifecycle selection is empty.
    """
    mappings = list(taxonomy.get("mappings") or [])
    dimensions = list(taxonomy.get("dimensions") or [])
    dim_keys = dimension_keys_with_mappings(mappings)
    sources = dimension_source_map(mappings)
    dim_name = {d.get("dimension_key"): d.get("name") for d in dimensions}

    selected_lifecycle = st.pills(
        "Lifecycle status",
        options=list(LIFECYCLE_ORDER),
        default=list(LIFECYCLE_DEFAULT_FILTER),
        selection_mode="multi",
        help=(
            "Filter the task list and overall charts. ARCHIVED is hidden by "
            "default; feature/initiative rollups still count archived cards."
        ),
        key="dashboard_lifecycle_filter",
    )
    if isinstance(selected_lifecycle, str):
        selected_lifecycle = [selected_lifecycle]
    selected_lifecycle = list(selected_lifecycle or [])
    if not selected_lifecycle:
        st.info("Select at least one lifecycle status to show tasks.")
        return None

    group_key: str | None = None
    taxonomy_filters: dict[str, set[str]] = {}

    if dim_keys:
        default_group = (
            DIM_INITIATIVE if DIM_INITIATIVE in dim_keys else dim_keys[0]
        )
        group_labels = {
            key: str(dim_name.get(key) or _dim_label(dimensions, key))
            for key in dim_keys
        }
        group_key = st.segmented_control(
            "Group by",
            options=dim_keys,
            default=default_group,
            format_func=lambda key: group_labels.get(key, key),
            help="Group rollup cards by any configured taxonomy dimension.",
            key="dashboard_group_dimension",
        )
        if group_key is None:
            group_key = default_group

        with st.expander("Taxonomy filters", expanded=False):
            st.caption(
                "Combine with lifecycle (e.g. OPEN + feature = Mobile). "
                "Leave a dimension empty to include all values."
            )
            cols = st.columns(min(len(dim_keys), 3) or 1)
            for index, key in enumerate(dim_keys):
                options = board_values_for_source(
                    sources.get(key, ""),
                    lists=lists or [],
                    labels=labels or [],
                    board_name=board_name,
                )
                if not options:
                    continue
                label = str(dim_name.get(key) or _dim_label(dimensions, key))
                with cols[index % len(cols)]:
                    picked = st.multiselect(
                        label,
                        options=options,
                        default=[],
                        key=f"dashboard_tax_filter_{key}",
                    )
                    if picked:
                        taxonomy_filters[key] = set(picked)

    return {
        "lifecycle_filter": set(selected_lifecycle),
        "group_dimension_key": group_key,
        "taxonomy_filters": taxonomy_filters or None,
        "mappings": mappings,
        "dimensions": dimensions,
        "dim_keys": dim_keys,
    }


__all__ = ["render_dashboard_filters"]
