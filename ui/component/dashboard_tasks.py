"""Visible-task table showing all taxonomy values per card."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_visible_tasks(
    tasks: list[dict[str, Any]],
    *,
    group_dimension_key: str | None,
    dimensions: list[dict[str, Any]],
) -> None:
    """Show filtered tasks with every mapped value for each dimension (FR3.4)."""
    if not tasks:
        return

    dim_names = {
        str(d.get("dimension_key")): str(d.get("name") or d.get("dimension_key"))
        for d in dimensions
    }
    group_label = dim_names.get(group_dimension_key or "", "Group")

    extra_keys: list[str] = []
    for task in tasks:
        for key in task.get("taxonomy") or {}:
            if key not in extra_keys and key != group_dimension_key:
                extra_keys.append(key)

    col_order = ["Task", "Lifecycle", group_label] + [
        dim_names.get(key, key) for key in extra_keys
    ]
    rows: list[dict[str, str]] = []
    for task in tasks:
        tax = task.get("taxonomy") or {}
        row = {
            "Task": str(task.get("name") or ""),
            "Lifecycle": str(task.get("lifecycleStatus") or ""),
            group_label: str(task.get("group_values") or ""),
        }
        for key in extra_keys:
            row[dim_names.get(key, key)] = str(tax.get(key) or "")
        rows.append(row)

    with st.expander(f"Visible tasks ({len(rows)})", expanded=False):
        st.caption(
            "Cards with multiple labels on the same dimension list every value."
        )
        st.dataframe(
            rows, hide_index=True, width="stretch", column_order=col_order
        )


__all__ = ["render_visible_tasks"]
