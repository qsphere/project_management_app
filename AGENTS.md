# AGENTS.md — Trello board tools

Guidance for AI agents working in this project. Prefer this file over generic advice when they conflict.

## What this app is

Small Python tool that creates and manages Trello cards from Excel, plus a Streamlit UI with an initiative dashboard.

- **Clients (strict external I/O):** `clients/` — only package that may call remote APIs or the DB (`requests` → Trello; `psycopg` → Neon; `resend` → Resend email)
- **Constants:** `constants/` — static data only (palettes, page lists, CSS, Excel aliases, status heuristics)
- **Helpers:** `functions/` — pure helpers and domain builders (no Streamlit, no raw HTTP)
- **Orchestration:** `services/` — thin wrappers over clients + domain (no Streamlit, no raw HTTP)
- **CLI entry:** `trello_cli.py` — argparse + secrets.toml only; calls `functions` / `services`
- **UI entry:** `app.py` — page config, nav, sidebar hook, page dispatch
- **UI modules (Streamlit-only):** `ui/views/`, `ui/tabs/`, `ui/component/`

Keep Trello HTTP in `clients/`. Keep domain math and Excel parsing in `functions/`. Keep import orchestration that needs `TrelloClient` in `services/`. Keep Streamlit rendering and session/widget state under `ui/` only — every non-empty module there must use Streamlit. Project `.py` files must stay ≤ 250 lines. Top-level page modules live in `ui/views/` (not a top-level `pages/`) so `streamlit run app.py` does not auto-register Streamlit multipage routes.

## Domain model (important)

The connected board is interpreted as:

| Trello concept | App meaning |
| --- | --- |
| **Cards / Lists / Labels / Boards** | Taxonomy field sources (raw names = dimension values) |
| **Card** | Task |
| **Card flags** | Status via derived `lifecycleStatus` (not list names) |

Dashboard Status pies always use derived `lifecycleStatus` from `compute_lifecycle_status()` (`functions/status.py`), recomputed on every sync (never stored). Precedence (first match wins):

- **ARCHIVED** — `closed == true`
- **CLOSED** — `closed == false` and due is set and `dueComplete == true`
- **OPEN** — otherwise (including cards with no due date)

**Initiative grouping:** each taxonomy dimension maps 1:1 to a Trello field (Cards, Lists, Labels, or Boards). Dashboard groups by that field’s raw names (defaults: Feature→Labels, Initiative→Labels, Status→Lists). Cards with no value follow the workspace unmapped policy (show as `Unmapped` or exclude).

**Dashboard filters (FR3):** lifecycleStatus is always available; default view is OPEN + CLOSED (ARCHIVED hidden until toggled). Group/filter by any configured taxonomy dimension independently; combine with lifecycle (e.g. OPEN + feature = Mobile). Cards with multiple labels on a labels-mapped dimension contribute every value (multi-group + task table). Feature/initiative completion = (CLOSED + ARCHIVED) ÷ total mapped cards — archived stay in rollup math even when hidden from the visible task list. Rollups stay visible at 100% (no auto-collapse; explicit close-out is a future to-do).

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
│   ├── trello_cards.py         # card create / update / delete
│   ├── neon.py                 # Neon Postgres (psycopg) — sole DB surface
│   ├── neon_entity.py          # entity configuration table mixin
│   ├── neon_workspace.py       # workspaces + members mixin
│   ├── neon_taxonomy.py        # taxonomy dimensions + mappings mixin
│   └── resend.py               # Resend email API — sole email surface
├── constants/                  # STRICT: sole place for static constants
│   ├── pages.py                # PAGES = Dashboard, Cards, Labels, Settings
│   ├── colors.py               # COLOR_SWATCH, LABEL_COLORS, PALETTE_HUES
│   ├── styles.py               # NAV_CSS, CONNECTIONS_CSS, DASHBOARD_CSS
│   ├── config_styles.py        # CONFIGURATION_CSS
│   ├── entity_config.py        # default Initiative→Labels, Status→Lists
│   ├── taxonomy.py             # default dims, field sources, unmapped policy
│   ├── links.py                # Trello guide, GitHub, privacy URLs
│   ├── excel.py                # COLUMN_ALIASES, TEMPLATE_COLUMNS
│   └── status.py               # LIST_PALETTE, LIFECYCLE_* buckets/colors
├── functions/                  # pure helpers + domain (no Streamlit)
│   ├── env.py                  # env(), load_secrets(), SCRIPT_DIR, SECRETS_PATH
│   ├── dates.py                # card/Excel/Trello date parse/format
│   ├── cards.py                # card choice labels + filter_cards
│   ├── charts.py               # Altair burndown/donut + status legend HTML
│   ├── status.py               # compute_lifecycle_status
│   ├── excel.py                # load/normalize Excel, template bytes
│   ├── label_dashboard.py      # build_label_dashboard
│   ├── burndown.py             # card_lifecycle + build_burndown_series
│   ├── dashboard_breakdown.py  # lifecycle pie breakdown helpers
│   ├── dashboard_rollups.py    # feature/initiative rollup rows + completion %
│   ├── taxonomy.py             # field resolve, import validate
│   ├── taxonomy_filter.py      # annotate/filter by taxonomy + lifecycle
│   └── initiative_dashboard.py # build_initiative_dashboard
├── services/                  # orchestration (no Streamlit, no raw HTTP/DB)
│   ├── trello.py               # TrelloClient wrappers (connect, cards, labels, dashboards)
│   ├── neon.py                 # NeonClient wrappers (connect, ping)
│   ├── auth.py                 # account create / sign-in (Neon + welcome email)
│   ├── config.py               # named Trello connections CRUD (Neon)
│   ├── entity_config.py        # legacy Initiative/Status configs (unused by dashboard)
│   ├── workspace.py            # personal workspace ensure + unmapped policy
│   ├── taxonomy.py             # taxonomy dimension/mapping CRUD
│   ├── taxonomy_io.py          # taxonomy JSON import/export + dashboard load
│   ├── email.py                # ResendClient wrappers (welcome email)
│   ├── excel.py                # process_tasks / UI import helpers
│   └── __init__.py             # re-exports
├── trello_cli.py               # CLI entry only (Excel import)
├── app.py                      # Streamlit entry: config, nav, sidebar, page dispatch
├── ui/                         # STRICT: Streamlit-only UI package
│   ├── views/
│   │   ├── dashboard.py        # initiative dashboard (taxonomy-driven)
│   │   ├── cards.py            # Cards page shell (Manage + Import tabs)
│   │   ├── labels.py           # Labels page
│   │   ├── settings.py         # Settings page (Connections + Configuration tabs)
│   ├── tabs/
│   │   ├── manage.py           # Cards → Manage (filters, table, edit)
│   │   ├── import_cards.py     # Cards → Import (upload, preview, create)
│   │   ├── settings_connections.py  # Settings → Connections
│   │   └── configuration.py    # Settings → Configuration
│   └── component/
│       ├── sidebar.py          # active connection + create delay
│       ├── auth.py             # sign-in / manage account
│       ├── trello_config_state.py  # session helpers for active connection
│       ├── connection_dialog.py    # add/edit connection modal
│       ├── connection_list.py      # connection cards + empty state
│       ├── taxonomy_dialogs.py     # add/rename taxonomy dimension
│       ├── taxonomy_dimensions.py  # dimensions + unmapped policy UI
│       ├── taxonomy_mappings.py    # dimension → Trello field radios
│       ├── taxonomy_import_export.py  # taxonomy JSON download/upload
│       ├── dashboard_filters.py    # lifecycle + taxonomy group/filter controls
│       ├── dashboard_tasks.py      # visible task table (multi-value dims)
│       ├── footer.py               # page footer
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
├── .streamlit/
│   ├── secrets.toml.example    # template only
│   └── secrets.toml            # local secrets — never commit
└── README.md
```

Do not edit `.venv/` or commit `.streamlit/secrets.toml`. Static constants must live under `constants/` only. Non-Streamlit code must not live under `ui/`.

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

CLI flags override `.streamlit/secrets.toml` when provided (`--board-id`, `--list-id`, `--sheet`).

## Secrets

Credentials live in `.streamlit/secrets.toml` ([Streamlit secrets management](https://docs.streamlit.io/develop/concepts/connections/secrets-management)). Root-level keys are loaded into `os.environ` via `load_secrets()` (UI + CLI) and are also available as `st.secrets["KEY"]` when Streamlit runs.

| Variable | Required | Role |
| --- | --- | --- |
| `TRELLO_API_KEY` | Yes | Power-Up API key |
| `TRELLO_TOKEN` | Yes | Read/write token |
| `TRELLO_BOARD_ID` | Yes* | Default board (*or pass in UI/CLI) |
| `TRELLO_LIST_ID` | No | Default list when a row has no List |
| `DATABASE_URL` | No* | Neon Postgres URL (*required for DB features; prefer pooled `-pooler` host) |
| `CREDENTIALS_ENCRYPTION_KEY` | No* | Fernet key for encrypted connection credentials |
| `RESEND_API_KEY` | No* | Resend API key for account emails |
| `RESEND_FROM_EMAIL` | No | Resend from address |

Auth is always query params `key` + `token` on `https://api.trello.com/1`. Never log full request URLs or params that include secrets. `clients.http.raise_for_status` exists specifically to avoid leaking credentials in error messages — keep that property. Never log `DATABASE_URL`. Signed-in users can save multiple named Trello connections on Settings → Connections (`app_trello_connections` in Neon). **Taxonomy mappings** live on the user’s personal workspace (`app_workspaces` / `app_taxonomy_*`): each dimension maps 1:1 to a Trello field (cards / lists / labels / boards); raw field names are the dashboard values (defaults: feature→labels, initiative→labels, status→lists; custom dims allowed). Unmapped policy is show-as-`Unmapped` or exclude. JSON export/import is supported. Status chart slices always use derived `lifecycleStatus`. `.streamlit/secrets.toml` remains the default/fallback for Trello credentials.

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
2. **Strict clients package:** Only `clients/` may perform external HTTP or DB I/O. All Trello calls go through `TrelloClient` (`_get` / `_post` / `_put` / `_delete` in `clients/http.py`). All Postgres goes through `NeonClient` (`clients/neon.py` and mixins such as `clients/neon_entity.py`). All Resend email goes through `ResendClient` (`clients/resend.py`). Do not import `requests`, `psycopg`, or `resend` from `ui/`, `services/`, `functions/`, or `trello_cli.py`.
3. **Strict constants package:** Static constants live only under `constants/`. Do not add constant modules under `clients/`, `functions/`, `services/`, or `ui/`; import from `constants`.
4. **`services/` is orchestration, not HTTP/DB:** It orchestrates `clients.TrelloClient` / `clients.NeonClient` / `clients.ResendClient` + `functions` helpers. Do not reimplement Trello, SQL, or Resend there.
5. **Caches:** `lists_by_name`, `labels_by_name`, `members_by_name` are lazy. Invalidate label cache after create/update/delete (see `_invalidate_labels_cache`).
6. **Import path:** UI and CLI both use `load_tasks` → `process_tasks` (`functions/excel.py` → `services/excel.py`). Preserve dry-run behavior.
7. **Dashboard path:** `build_initiative_dashboard` / `build_label_dashboard` own the data shape; `ui/views/dashboard.py` and `ui/component/` only chart and lay out.
8. **Types:** Prefer `from __future__ import annotations` and explicit return types on new public functions.
9. **Dependencies:** Stick to `requirements.txt` (pandas, openpyxl, requests, streamlit, psycopg, resend, cryptography). Add Altair only if the UI already imports it for charts.
10. **File length:** Every project `.py` file ≤ 250 lines. Split by responsibility before finishing; do not minify to dodge the limit.

## UI pages

`app.py` dispatches; sidebar is `ui/component/sidebar.py`. Main nav (`constants/pages.py`):

1. **Dashboard** (`ui/views/dashboard.py`) — lifecycle + taxonomy filters, dimension rollups (needs connected client)
2. **Cards** (`ui/views/cards.py`) — Manage tab (`ui/tabs/manage.py`: filters, edit/move/delete, mass delete) and Import tab (`ui/tabs/import_cards.py`: upload `.xlsx`, preview, dry-run or create)
3. **Labels** (`ui/views/labels.py`) — breakdown + CRUD + color palette
4. **Settings** (`ui/views/settings.py`) — **Connections** tab (`ui/tabs/settings_connections.py`; Neon `app_trello_connections`) and **Configuration** tab (`ui/tabs/configuration.py`; workspace taxonomy dimensions, dimension→Trello field mappings, JSON import/export, unmapped policy; signed-in only)

When adding a page: register it in `PAGES` (`constants/pages.py`), add `ui/views/<name>.py`, wire the nav in `app.py`, and gate on `client is None` like the others (Settings gates on signed-in user instead).

## Safety

- Never commit `.streamlit/secrets.toml`, tokens, or API keys.
- Prefer dry-run when changing import or label-creation behavior.
- Destructive Trello ops (`delete_card`, `delete_cards`, `delete_label`) should stay behind explicit UI confirmation.
- Rate-limit creates and bulk deletes with the existing delay slider / CLI delay; do not fire unbounded card POSTs/DELETEs.

## When changing behavior

- **New card fields:** extend `COLUMN_ALIASES` (`constants/excel.py`), `process_tasks` (`services/excel.py`), and `TrelloClient.create_card` / `update_card` together; update README.
- **New dashboard metric:** compute in `functions/initiative_dashboard.py` (or related helpers), render in `ui/views/dashboard.py` / related components.
- **Taxonomy mappings:** extend `constants/taxonomy.py`, Neon taxonomy mixins, `functions/taxonomy.py`, and Settings → Configuration UI together; keep one Trello field per dimension.
