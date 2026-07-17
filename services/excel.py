"""Excel import helpers used by the UI and CLI (no Streamlit, no raw HTTP)."""

from __future__ import annotations

import time
from collections.abc import Callable
from io import BytesIO

import pandas as pd

from clients import TrelloClient
from functions.dates import format_date_field, format_due, format_pos
from functions.excel import (
    build_excel_template,
    cell_str,
    list_sheet_names,
    load_tasks,
)

ProgressCallback = Callable[[int, int, str], None]


def excel_template_bytes() -> bytes:
    return build_excel_template()


def read_sheet_names(buffer: BytesIO) -> list[str]:
    return list_sheet_names(buffer)


def read_tasks(buffer: BytesIO, sheet: str):
    return load_tasks(buffer, sheet)


def process_tasks(
    tasks: pd.DataFrame,
    client: TrelloClient,
    *,
    default_list_id: str | None,
    dry_run: bool = False,
    delay: float = 0.25,
    on_progress: ProgressCallback | None = None,
) -> tuple[int, int, list[str]]:
    """
    Validate or create cards for each task row.

    Returns (success_count, fail_count, log_lines).
    ``on_progress(done, total, message)`` is called after each row when set.
    """
    created = 0
    failed = 0
    logs: list[str] = []
    total = len(tasks)

    for done, (index, row) in enumerate(tasks.iterrows(), start=1):
        row_num = int(index) + 2  # header is row 1 in Excel
        name = cell_str(row.get("name"))
        assert name is not None
        verb = "Validating" if dry_run else "Creating"
        if on_progress is not None:
            on_progress(done - 1, total, f"{verb} {done}/{total}: {name}")

        try:
            list_id = client.resolve_list_id(cell_str(row.get("list")), default_list_id)
            label_ids, created_labels = client.resolve_label_ids(
                row.get("labels"),
                create_missing=not dry_run,
            )
            member_ids = client.resolve_member_ids(row.get("assignee"))
            due = format_due(row.get("due"))
            start = format_date_field(row.get("start"), field_name="start date")
            pos = format_pos(row.get("pos"))
            desc = cell_str(row.get("description")) or ""

            created_note = ""
            if created_labels:
                action = "would create" if dry_run else "created"
                created_note = f" [{action} label(s): {', '.join(created_labels)}]"

            if dry_run:
                logs.append(
                    f"[dry-run] row {row_num}: {name!r} "
                    f"→ list={list_id} labels={label_ids or '-'} "
                    f"members={member_ids or '-'} "
                    f"due={due or '-'} start={start or '-'} "
                    f"pos={pos if pos is not None else '-'}{created_note}"
                )
            else:
                card = client.create_card(
                    name=name,
                    id_list=list_id,
                    desc=desc,
                    due=due,
                    start=start,
                    pos=pos,
                    id_labels=label_ids,
                    id_members=member_ids,
                )
                logs.append(
                    f"Created row {row_num}: {name!r} → "
                    f"{card.get('shortUrl', card.get('id'))}{created_note}"
                )
                if delay > 0:
                    time.sleep(delay)

            created += 1
            status = f"{'Validated' if dry_run else 'Created'} {done}/{total}: {name}"
        except Exception as exc:
            failed += 1
            logs.append(f"Error on row {row_num} ({name!r}): {exc}")
            status = f"Failed {done}/{total}: {name}"

        if on_progress is not None:
            on_progress(done, total, status)

    return created, failed, logs


def run_import(
    tasks,
    client: TrelloClient,
    *,
    default_list_id: str | None,
    dry_run: bool,
    delay: float,
    on_progress: ProgressCallback | None = None,
):
    return process_tasks(
        tasks,
        client,
        default_list_id=default_list_id,
        dry_run=dry_run,
        delay=delay,
        on_progress=on_progress,
    )
