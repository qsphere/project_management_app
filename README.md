# Trello board tools

Manage a Trello board (initiative dashboard, cards, labels) with a Streamlit UI, and import cards from Excel via CLI.

## Setup

This project needs a virtual environment (system Python blocks global `pip install`):

```bash
cd trello_from_excel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `.venv` already exists and `python3 -m venv .venv` fails with a permission error, either activate it as-is or recreate it:

```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure credentials

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
| --- | --- | --- |
| `TRELLO_API_KEY` | Yes | From [Trello Power-Ups admin](https://trello.com/power-ups/admin) |
| `TRELLO_TOKEN` | Yes | Token with read/write access. Authorize at: `https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&name=TrelloBoardTools&key=YOUR_KEY` |
| `TRELLO_BOARD_ID` | Yes* | Default board ID |
| `TRELLO_LIST_ID` | No | Default list when a row has no `List` value |
| `DATABASE_URL` | No* | Neon Postgres connection string (*needed for DB features; prefer pooled URL) |
| `RESEND_API_KEY` | No* | Resend API key (*needed to email users on account creation) |
| `RESEND_FROM_EMAIL` | No | From address; defaults to `Project Management <onboarding@resend.dev>` |

\*Board ID can also be passed with `--board-id` on the CLI, or entered in the UI.

Get `DATABASE_URL` from the [Neon Console](https://console.neon.tech/) → your project → **Connect**. Keep `sslmode=require` (and `channel_binding=require` when present).

Get `RESEND_API_KEY` from [Resend API keys](https://resend.com/api-keys). The default `onboarding@resend.dev` sender only delivers to your Resend account email; verify your own domain for production.

## Excel format

Columns are matched case-insensitively (aliases accepted):

| Column | Required | Notes |
| --- | --- | --- |
| Name / Title / Task | Yes | Card title |
| Description / Desc | No | Card body |
| List | No | Must match a list name on the board |
| Labels | No | Comma-separated label **names** (not IDs). Missing names are created on the board with an unused color |
| Assignee / Members | No | Comma-separated board member **full names** or **usernames** (mapped to `idMembers`) |
| Due / Due Date | No | Excel date or ISO string |

## Streamlit UI

```bash
source .venv/bin/activate
streamlit run app.py
```

**Dashboard** (home) — initiative view of the connected board: labels are initiatives, cards are tasks, and lists map to status (To Do / In Progress / Done / Blocked / Archived). Shows overall burndown, status percentages, and a card per label with completion % and burndown to target.

**Cards** — **Manage** tab: filter open cards by list, due date range, label, and assignee; edit/move/delete one card, or multi-select and mass-delete with confirmation. **Import** tab: upload a `.xlsx` file, preview tasks, then **Dry run** or **Create cards**.

**Labels** — detailed label breakdown by list, plus create/rename/recolor/delete. The Excel `Labels` column uses label names; any name not already on the board is created automatically during import.

## CLI

```bash
source .venv/bin/activate

# Validate without creating cards
python trello_cli.py tasks.xlsx --dry-run

# Create cards
python trello_cli.py tasks.xlsx

# Optional flags
python trello_cli.py tasks.xlsx --sheet "Sheet1" --board-id BOARD_ID --list-id LIST_ID
```

CLI flags override values from `.env` when provided.
