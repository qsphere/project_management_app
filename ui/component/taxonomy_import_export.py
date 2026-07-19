"""Taxonomy JSON export / import controls."""

from __future__ import annotations

import json

import streamlit as st

from services.auth import AuthError
from services.taxonomy_io import export_taxonomy_json, import_taxonomy


def render_import_export(*, user_id: int | str) -> None:
    st.markdown("### Export / import")
    st.caption(
        "Download mappings as JSON for version control, or upload to copy "
        "across workspaces."
    )
    col_a, col_b = st.columns(2)
    with col_a:
        try:
            payload = export_taxonomy_json(user_id)
        except AuthError as exc:
            st.error(str(exc))
            payload = "{}"
        st.download_button(
            "Export JSON",
            data=payload,
            file_name="taxonomy_mappings.json",
            mime="application/json",
            width="stretch",
            key="tax_export_btn",
        )
    with col_b:
        uploaded = st.file_uploader(
            "Import JSON",
            type=["json"],
            key="tax_import_file",
            label_visibility="collapsed",
        )
        replace = st.checkbox(
            "Replace existing mappings",
            value=True,
            key="tax_import_replace",
        )
        if uploaded is not None and st.button(
            "Import", type="primary", key="tax_import_btn", width="stretch"
        ):
            try:
                raw = json.loads(uploaded.getvalue().decode("utf-8"))
                import_taxonomy(user_id=user_id, payload=raw, replace=replace)
                st.success("Taxonomy imported.")
                st.rerun()
            except (AuthError, ValueError, json.JSONDecodeError) as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Import failed: {exc}")
