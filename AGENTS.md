# AGENTS.md — Trello board tools

Guidance for AI agents working in this project. Prefer this file over generic advice when they conflict.

## What this app is

Small Python tool that creates and manages Trello cards from Excel, plus a Streamlit UI with an initiative dashboard.

- **Clients (strict external HTTP):** `clients/` — only package that may call remote APIs (`requests` → Trello)
- **Constants:** `constants/` — static data only (palettes, page lists, CSS, Excel aliases, status heuristics)
- **Helpers:** `functions/` — pure helpers and domain builders (no Streamlit, no raw HTTP)
- **Orchestration:** `services/` — thin wrappers over clients + domain (no Streamlit, no raw HTTP)
- **CLI entry:** `trello_cli.py` — argparse + dotenv only; calls `functions` / `services`
- **UI entry:** `app.py` — page config, nav, sidebar hook, page dispatch
- **UI modules (Streamlit-only):** `ui/views/`, `ui/tabs/`, `ui/component/`

Keep Trello HTTP in `clients/`. Keep domain math and Excel parsing in `functions/`. Keep import orchestration that needs `TrelloClient` in `services/`. Keep Streamlit rendering and session/widget state under `ui/` only — every non-empty module there must use Streamlit. Project `.py` files must stay ≤ 250 lines. Top-level page modules live in `ui/views/` (not a top-level `pages/`) so `streamlit run app.py` does not auto-register Streamlit multipage routes.

## Domain model (important)

The connected board is interpreted as:

| Trello concept | App meaning |
| --- | --- |
| **Label** | Initiative |
| **Card** | Task |
| **List name** | Status (via keyword heuristics) |

Status buckets from `classify_list_status()` (`functions/status.py`; regexes in `constants/status.py`):

- **Archived** — card `closed` or list name matches archive keywords
- **Done** — done / complete / closed / shipped / finished
- **Blocked** — block / blocked / waiting / on hold / stuck
- **In Progress** — progress / doing / wip / active / review / qa / testing
- **To Do** — everything else

Changing those regexes changes dashboard semantics for every board. Document why if you edit them.

## Layout

`ui/` is **Streamlit-only** (non-empty modules must import Streamlit). Use `ui/views/` (not a top-level `pages/`) so Streamlit does **not** auto-register multipage routes when the entry is `app.py`.

```
trello_from_excel/
├── clients/                    # STRICT: sole place for external HTTP
│   ├── __init__.py             # exports TrelloClient, TRELLO_API
│   ├── http.py                 # session, auth, _get/_post/_put/_delete
│   ├── trello.py               # composed TrelloClient
│   ├── trello_board.py         # lists / cards reads / members / resolve ids
│   ├── trello_labels.py        # label CRUD + resolve/create missing
│   └── trello_cards.py         # card create / update / delete
├── constants/                  # STRICT: sole place for static constants
│   ├── pages.py                # PAGES = Dashboard, Cards, Labels
│   ├── colors.py               # COLOR_SWATCH, LABEL_COLORS, PALETTE_HUES
│   ├── styles.py               # NAV_CSS, DASHBOARD_CSS
│   ├── excel.py                # COLUMN_ALIASES, TEMPLATE_COLUMNS
│   └── status.py               # LIST_PALETTE, STATUS_*, status regexes
├── functions/                  # pure helpers + domain (no Streamlit)
│   ├── env.py                  # env(), SCRIPT_DIR
│   ├── dates.py                # card/Excel/Trello date parse/format
│   ├── cards.py                # card choice labels + filter_cards
│   ├── charts.py               # Altair burndown/donut + status legend HTML
│   ├── status.py               # classify_list_status
│   ├── excel.py                # load/normalize Excel, template bytes
│   ├── label_dashboard.py      # build_label_dashboard
│   ├── burndown.py             # card_lifecycle + build_burndown_series
│   └── initiative_dashboard.py # build_initiative_dashboard
├── services/                  # orchestration (no Streamlit, no raw HTTP)
│   ├── trello.py               # TrelloClient wrappers (connect, cards, labels, dashboards)
│   ├── excel.py                # process_tasks / UI import helpers
│   └── __init__.py             # re-exports
├── trello_cli.py               # CLI entry only (Excel import)
├── app.py                      # Streamlit entry: config, nav, sidebar, page dispatch
├── ui/                         # STRICT: Streamlit-only UI package
│   ├── views/
│   │   ├── dashboard.py        # initiative dashboard page
│   │   ├── cards.py            # Cards page shell (Manage + Import tabs)
│   │   └── labels.py           # Labels page
│   ├── tabs/
│   │   ├── manage.py           # Cards → Manage (filters, table, edit)
│   │   └── import_cards.py     # Cards → Import (upload, preview, create)
│   └── component/
│       ├── sidebar.py          # credentials + defaults + create delay
│       ├── initiative_card.py  # one initiative card on Dashboard
│       ├── color_selector.py   # label color palette + dashboard CSS inject
│       ├── cards_filters.py    # list / due / label / assignee filters
│       ├── cards_table.py      # card table + selection
│       ├── cards_edit.py       # edit / move / delete one card
│       ├── cards_mass_delete.py# bulk delete confirmation
│       ├── label_overview.py   # label breakdown table/charts
│       └── label_crud.py       # label create / update / delete
├── scripts/
│   └── check_app_streamlit_only.py
├── requirements.txt
├── .env.example                # template only
├── .env                        # local secrets — never commit
└── README.md
```

Do not edit `.venv/` or commit `.env`. Static constants must live under `constants/` only. Non-Streamlit code must not live under `ui/`.

## Setup & commands

Always use the project venv (system Python may block global installs):

```bash
cd trello_from_excel
source .venv/bin/activate
pip install -r requirements.txt

# UI
streamlit run app.py

# CLI
python trello_cli.py tasks.xlsx --dry-run
python trello_cli.py tasks.xlsx

# Layout check (ui/ must be Streamlit-only)
python scripts/check_app_streamlit_only.py
```

CLI flags override `.env` when provided (`--board-id`, `--list-id`, `--sheet`).

## Environment

| Variable | Required | Role |
| --- | --- | --- |
| `TRELLO_API_KEY` | Yes | Power-Up API key |
| `TRELLO_TOKEN` | Yes | Read/write token |
| `TRELLO_BOARD_ID` | Yes* | Default board (*or pass in UI/CLI) |
| `TRELLO_LIST_ID` | No | Default list when a row has no List |

Auth is always query params `key` + `token` on `https://api.trello.com/1`. Never log full request URLs or params that include secrets. `clients.http.raise_for_status` exists specifically to avoid leaking credentials in error messages — keep that property.

Authorize a token (replace `YOUR_KEY`):
`https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&name=TrelloBoardTools&key=YOUR_KEY`

## Excel import contract

Columns are case-insensitive via `COLUMN_ALIASES` (`constants/excel.py`):

| Field | Aliases | Notes |
| --- | --- | --- |
| name | name, title, task, card, card_name | Required |
| description | description, desc, details, body | |
| list | list, list_name, column, status | Must match an open list name |
| labels | labels, label, tags, tag | Comma-separated **names**; missing names are created |
| assignee | assignee(s), member(s), assigned_to, assign | Full names or usernames; must already be board members |
| due | due, due_date, deadline, date | Excel date or ISO |
| start | start, start_date | |
| pos | pos, position | `top`, `bottom`, or number |

Prefer extending `COLUMN_ALIASES` over one-off column handling in the UI.

## Architecture rules

1. **`ui/` is Streamlit-only:** Every non-empty module under `ui/` must use Streamlit. Pure helpers → `functions/`; constants → `constants/`; orchestration → `services/`; HTTP → `clients/`. Enforce with `python scripts/check_app_streamlit_only.py`.
2. **Strict clients package:** Only `clients/` may perform external HTTP. All Trello calls go through `TrelloClient` (`_get` / `_post` / `_put` / `_delete` in `clients/http.py`). Do not import `requests` for Trello from `ui/`, `services/`, `functions/`, or `trello_cli.py`.
3. **Strict constants package:** Static constants live only under `constants/`. Do not add constant modules under `clients/`, `functions/`, `services/`, or `ui/`; import from `constants`.
4. **`services/` is orchestration, not HTTP:** It orchestrates `clients.TrelloClient` + `functions` helpers. Do not reimplement Trello calls there.
5. **Caches:** `lists_by_name`, `labels_by_name`, `members_by_name` are lazy. Invalidate label cache after create/update/delete (see `_invalidate_labels_cache`).
6. **Import path:** UI and CLI both use `load_tasks` → `process_tasks` (`functions/excel.py` → `services/excel.py`). Preserve dry-run behavior.
7. **Dashboard path:** `build_initiative_dashboard` / `build_label_dashboard` own the data shape; `ui/views/dashboard.py` and `ui/component/` only chart and lay out.
8. **Types:** Prefer `from __future__ import annotations` and explicit return types on new public functions.
9. **Dependencies:** Stick to `requirements.txt` (pandas, openpyxl, requests, python-dotenv, streamlit). Add Altair only if the UI already imports it for charts.
10. **File length:** Every project `.py` file ≤ 250 lines. Split by responsibility before finishing; do not minify to dodge the limit.

## UI pages

`app.py` dispatches; sidebar is `ui/component/sidebar.py`. Main nav (`constants/pages.py`):

1. **Dashboard** (`ui/views/dashboard.py`) — initiative burndown / status (needs connected client)
2. **Cards** (`ui/views/cards.py`) — Manage tab (`ui/tabs/manage.py`: filters, edit/move/delete, mass delete) and Import tab (`ui/tabs/import_cards.py`: upload `.xlsx`, preview, dry-run or create)
3. **Labels** (`ui/views/labels.py`) — breakdown + CRUD + color palette

When adding a page: register it in `PAGES` (`constants/pages.py`), add `ui/views/<name>.py`, wire the nav in `app.py`, and gate on `client is None` like the others.

## Safety

- Never commit `.env`, tokens, or API keys.
- Prefer dry-run when changing import or label-creation behavior.
- Destructive Trello ops (`delete_card`, `delete_cards`, `delete_label`) should stay behind explicit UI confirmation.
- Rate-limit creates and bulk deletes with the existing delay slider / CLI delay; do not fire unbounded card POSTs/DELETEs.

## When changing behavior

- **New card fields:** extend `COLUMN_ALIASES` (`constants/excel.py`), `process_tasks` (`services/excel.py`), and `TrelloClient.create_card` / `update_card` together; update README.
- **New dashboard metric:** compute in `functions/initiative_dashboard.py` (or related helpers), render in `ui/views/dashboard.py` / related components.
- **Status keywords:** update the regexes in `constants/status.py` and README status notes.
