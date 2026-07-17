from __future__ import annotations

from io import BytesIO

import streamlit as st

from services import (
    connected_client,
    excel_template_bytes,
    read_sheet_names,
    read_tasks,
    run_import,
)


def render_import_tab(
    *,
    api_key: str,
    token: str,
    board_id: str,
    selected_list_id: str | None,
    delay: float,
) -> None:
    uploaded = st.file_uploader("Excel file (.xlsx)", type=["xlsx"])

    st.download_button(
        label="Download Excel template",
        data=excel_template_bytes(),
        file_name="trello_cards_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )

    if not uploaded:
        st.markdown(
            """
**Expected columns** → [Trello `POST /cards`](https://developer.atlassian.com/cloud/trello/rest/api-group-cards/#api-cards-post)

| Excel column | Trello API field | Required |
| --- | --- | --- |
| Name / Title / Task | `name` | Yes |
| Description / Desc | `desc` | No |
| List | `idList` (resolved from list name) | No (uses default list) |
| Labels | `idLabels` (from label **names**; missing labels are created) | No |
| Assignee / Members | `idMembers` (from member full name or username) | No |
| Due / Due Date | `due` | No |
| Start | `start` | No |
| Position / Pos | `pos` (`top`, `bottom`, or a number) | No |
"""
        )
        st.caption(
            "Cards are created with `key`/`token` as query params and card fields in a JSON body. "
            "Put comma-separated label **names** in Labels (missing names are created). "
            "Put board member **full names** or **usernames** in Assignee — they must already "
            "be members of the board."
        )
        return

    file_bytes = uploaded.getvalue()
    buffer = BytesIO(file_bytes)

    try:
        sheets = read_sheet_names(buffer)
    except Exception as exc:
        st.error(f"Could not read workbook: {exc}")
        return

    sheet = st.selectbox("Sheet", sheets, index=0)

    try:
        buffer.seek(0)
        tasks = read_tasks(buffer, sheet)
    except Exception as exc:
        st.error(f"Could not load tasks: {exc}")
        return

    st.subheader(f"Preview · {len(tasks)} task(s)")
    if tasks.empty:
        st.warning("No tasks found in this sheet.")
        return

    st.dataframe(tasks, width="stretch")

    col_dry, col_create = st.columns(2)
    dry_clicked = col_dry.button("Dry run", width="stretch")
    create_clicked = col_create.button(
        "Create cards",
        type="primary",
        width="stretch",
    )

    if dry_clicked or create_clicked:
        if not api_key or not token:
            st.error("API key and token are required.")
            return
        if not board_id:
            st.error("Board ID is required.")
            return
        if not selected_list_id and "list" not in tasks.columns:
            st.error("Pick a default list, or include a List column in the spreadsheet.")
            return

        dry_run = bool(dry_clicked)
        client = connected_client(api_key, token, board_id)
        if client is None:
            st.error("Could not connect to Trello.")
            return

        total = len(tasks)
        progress = st.progress(
            0,
            text=("Validating…" if dry_run else "Creating cards…") + f" 0/{total}",
        )

        def _on_progress(done: int, total_count: int, message: str) -> None:
            fraction = done / total_count if total_count else 1.0
            progress.progress(min(fraction, 1.0), text=message)

        created, failed, logs = run_import(
            tasks,
            client,
            default_list_id=selected_list_id,
            dry_run=dry_run,
            delay=delay,
            on_progress=_on_progress,
        )

        if failed:
            st.error(f"{'Validated' if dry_run else 'Created'} {created}; {failed} failed.")
        else:
            st.success(f"{'Validated' if dry_run else 'Created'} {created} card(s).")

        st.code("\n".join(logs) if logs else "(no output)", language="text")
