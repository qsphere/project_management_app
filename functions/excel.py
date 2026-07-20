from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd

from constants.excel import COLUMN_ALIASES, TEMPLATE_COLUMNS
from functions.dates import format_card_date
from functions.subtasks import encode_subtasks_cell


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map Excel headers to canonical field names using COLUMN_ALIASES."""
    rename: dict[str, str] = {}
    used_targets: set[str] = set()

    for original in df.columns:
        key = str(original).strip().lower().replace(" ", "_")
        for target, aliases in COLUMN_ALIASES.items():
            if key in aliases and target not in used_targets:
                rename[original] = target
                used_targets.add(target)
                break

    return df.rename(columns=rename)


def cell_str(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def _workbook_bytes(rows: list[dict[str, Any]]) -> bytes:
    frame = pd.DataFrame(rows, columns=list(TEMPLATE_COLUMNS))
    buffer = BytesIO()
    frame.to_excel(buffer, index=False, sheet_name="Tasks")
    return buffer.getvalue()


def build_excel_template() -> bytes:
    """Return an .xlsx workbook with the expected headers and one example row."""
    return _workbook_bytes(
        [
            {
                "Name": "Example card title",
                "Description": "Optional card description",
                "List": "To Do",
                "Labels": "Bug, High Priority",
                "Assignee": "Jane Doe",
                "Due": "2026-08-01",
                "Start": "2026-07-20",
                "Position": "top",
                "Subtasks": "Prep: Draft outline | Review notes; Ship: Deploy",
            }
        ]
    )


def card_to_template_row(
    card: dict,
    *,
    list_id_to_name: dict[str, str],
    label_names: dict[str, str],
    member_names: dict[str, str],
) -> dict[str, str]:
    """Map a Trello card dict to one import-template row."""
    labels = ", ".join(
        label_names.get(lid, lid) for lid in card.get("idLabels") or []
    )
    assignees = ", ".join(
        member_names.get(mid, mid) for mid in card.get("idMembers") or []
    )
    pos = card.get("pos")
    return {
        "Name": card.get("name") or "",
        "Description": card.get("desc") or "",
        "List": list_id_to_name.get(card.get("idList") or "", ""),
        "Labels": labels,
        "Assignee": assignees,
        "Due": format_card_date(card.get("due")),
        "Start": format_card_date(card.get("start")),
        "Position": "" if pos is None or pos == "" else str(pos),
        "Subtasks": encode_subtasks_cell(card.get("checklists") or []),
    }


def build_cards_excel(
    cards: list[dict],
    *,
    list_id_to_name: dict[str, str],
    label_names: dict[str, str],
    member_names: dict[str, str],
) -> bytes:
    """Export cards as an .xlsx matching the import template columns."""
    rows = [
        card_to_template_row(
            card,
            list_id_to_name=list_id_to_name,
            label_names=label_names,
            member_names=member_names,
        )
        for card in cards
    ]
    return _workbook_bytes(rows)


def list_sheet_names(excel_source: str | Path | Any) -> list[str]:
    workbook = pd.ExcelFile(excel_source)
    return list(workbook.sheet_names)


def load_tasks(excel_source: str | Path | Any, sheet: str | int | None) -> pd.DataFrame:
    read_kwargs: dict[str, Any] = {}
    if sheet is not None:
        read_kwargs["sheet_name"] = sheet

    df = pd.read_excel(excel_source, **read_kwargs)
    if isinstance(df, dict):
        raise ValueError("Multiple sheets returned; pass --sheet to select one.")

    df = normalize_columns(df)
    if "name" not in df.columns:
        raise ValueError(
            "Excel file must include a Name/Title/Task column. "
            f"Found columns: {', '.join(map(str, df.columns))}"
        )

    # Drop fully empty rows and rows without a card name
    df = df.dropna(how="all")
    df = df[df["name"].apply(lambda v: cell_str(v) is not None)].copy()
    return df.reset_index(drop=True)
