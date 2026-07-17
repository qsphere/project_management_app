from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd

from constants.excel import COLUMN_ALIASES, TEMPLATE_COLUMNS


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


def build_excel_template() -> bytes:
    """Return an .xlsx workbook with the expected headers and one example row."""
    example = pd.DataFrame(
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
            }
        ],
        columns=list(TEMPLATE_COLUMNS),
    )
    buffer = BytesIO()
    example.to_excel(buffer, index=False, sheet_name="Tasks")
    return buffer.getvalue()


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
