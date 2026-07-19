#!/usr/bin/env python3
"""
CLI: create Trello cards from rows in an Excel spreadsheet.

Credentials and defaults come from `.streamlit/secrets.toml`
(see `.streamlit/secrets.toml.example`). Domain logic lives under
``functions/`` and ``services/``; this file is the CLI entry only.

Example:
  python trello_cli.py tasks.xlsx --dry-run
  python trello_cli.py tasks.xlsx --board-id abc123
"""

from __future__ import annotations

import argparse
import os
import sys

from services.excel import process_tasks
from clients import TrelloClient
from functions.env import SECRETS_PATH, load_secrets
from functions.excel import load_tasks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create Trello cards from an Excel spreadsheet.",
    )
    parser.add_argument("excel_path", help="Path to the .xlsx file")
    parser.add_argument(
        "--sheet",
        default=None,
        help="Sheet name or 0-based index (default: first sheet)",
    )
    parser.add_argument(
        "--board-id",
        default=None,
        help="Trello board ID (or set TRELLO_BOARD_ID in secrets.toml)",
    )
    parser.add_argument(
        "--list-id",
        default=None,
        help=(
            "Default list ID when a row has no List value "
            "(or set TRELLO_LIST_ID in secrets.toml)"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without creating cards",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.25,
        help="Seconds to wait between card creates (default: 0.25)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    load_secrets()

    parser = build_parser()
    args = parser.parse_args(argv)

    # Re-read defaults after secrets load so CLI still wins when flags are
    # passed, but secrets.toml values apply when flags are omitted.
    if args.board_id is None:
        args.board_id = os.getenv("TRELLO_BOARD_ID")
    if args.list_id is None:
        args.list_id = os.getenv("TRELLO_LIST_ID")

    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")

    if not api_key or not token:
        print(
            "Error: Set TRELLO_API_KEY and TRELLO_TOKEN in "
            f"{SECRETS_PATH} or in the environment.",
            file=sys.stderr,
        )
        return 1

    if not args.board_id:
        print(
            "Error: Pass --board-id or set TRELLO_BOARD_ID in secrets.toml.",
            file=sys.stderr,
        )
        return 1

    sheet: str | int | None = args.sheet
    if sheet is not None and str(sheet).isdigit():
        sheet = int(sheet)

    try:
        tasks = load_tasks(args.excel_path, sheet)
    except Exception as exc:
        print(f"Error reading Excel file: {exc}", file=sys.stderr)
        return 1

    if tasks.empty:
        print("No tasks found in the spreadsheet.")
        return 0

    client = TrelloClient(api_key, token, args.board_id)
    created, failed, logs = process_tasks(
        tasks,
        client,
        default_list_id=args.list_id,
        dry_run=args.dry_run,
        delay=args.delay,
    )

    for line in logs:
        stream = sys.stderr if line.startswith("Error") else sys.stdout
        print(line, file=stream)

    action = "Validated" if args.dry_run else "Created"
    print(f"\n{action} {created} card(s); {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
