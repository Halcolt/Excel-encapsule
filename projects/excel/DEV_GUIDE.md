- Filters: per-column dropdown (?) opens a searchable, multi-select list of distinct values; supports filtering blanks; multiple columns can be filtered together
# Excel Viewer – Developer Guide

Purpose
- Provide a simple web UI for viewing Excel/CSV, light editing in the browser, and exporting to `.xlsx`.

Stack
- Flask (app), Gunicorn (server), pandas/openpyxl (parse/export), HTML templates (no heavy front‑end)

Run
- `cd projects/excel`
- `docker compose up --build`
- Open `http://localhost:8080`

Config (env)
- `PORT` (default 8000)
- `MAX_UPLOAD_MB` (default 16)
- `UPLOAD_TTL_HOURS` (default 24)
- `FLASK_SECRET_KEY` (default `dev` – set in production)

Features
- Upload multiple files
- Per-file �Select all sheets / Clear� controls on the selection screen
- Select multiple sheets across files
- Tabbed viewing of selected sheets with Excel-style row/column markers, Home shortcut, and Ctrl multi-select rows/columns (selection readouts)
- Inline edits (contentEditable) on table cells
- Export selected sheets to `.xlsx`
- i18n (EN/VI) with ENG/VIE pill switch
- Filters: per-column dropdown (▾) opens a searchable, multi-select list of distinct values; supports filtering blanks; multiple columns can be filtered together
- Large tables scroll in-panel (no page overflow)

Routes
- `GET /` – upload UI (client-side add/remove files)
- `POST /upload` – saves files under a token (temp dir)
- `GET /select/<token>` – choose sheets across uploaded files
- `POST /render_multi` – render selected sheets in tabs (editable)
- `POST /export` – returns generated `.xlsx` built from edited tables
- `GET /set-lang/<lang>` – switch language; safe redirect to a GET route

Internals
- Temp uploads root: under system temp or `UPLOAD_ROOT` env; per upload token
- Cleanup: daemon thread removes token directories older than `UPLOAD_TTL_HOURS`
- Export: builds Excel in‑memory with `openpyxl` via `pandas.ExcelWriter`
- Sheet names are sanitized and deduplicated
- Rendering: DataFrames are blank-normalized (`fillna("")`) and `to_html(..., na_rep="")` to avoid “NaN” display

I18n
- Translations live in `app/i18n/en.json` and `app/i18n/vi.json`
- `t(key)` is injected into templates via a context processor

Future Refactor (clean architecture)
- Introduce services and ports (storage/parser/export) with adapters
- App factory + Blueprint for web routes
- Add CSRF tokens; optional auth; CSV encoding/delimiter detection; drag‑drop

Testing
- Add unit tests for export shape and sheet name sanitization
- Route smoke tests for upload/select/render/export

Dev Loop
- Auto-reload service `dev` is available:
  - `docker compose up -d dev` (from `projects/excel`)
  - Edits in `app/` reload Gunicorn; rebuild when dependencies change
