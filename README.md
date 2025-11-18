# Workspace: Notion + Excel Viewer (Dockerized)

This workspace hosts multiple Dockerized subprojects:
- Notion tooling for documentation and project management
- Excel Viewer web app for non‑Excel users to view/edit/export data

## Prerequisites
- Docker Desktop (WSL2 engine on Windows)
- For Notion tools: Notion Internal Integration token

## Quick Start

Notion tools
1. Copy env and add token:
   - PowerShell: `Copy-Item .env.example .env`
   - Edit `.env` and set `NOTION_TOKEN=secret_xxx`
2. Build: `cd projects/notion && docker compose build`
3. Test: `docker compose run --rm app python notion_test.py`

Excel Viewer
1. `cd projects/excel`
2. `docker compose up --build`
3. Open `http://localhost:8080` → upload files → pick sheets → edit → export

## Subprojects

Notion (`projects/notion`)
- Python 3.12 image; `notion-client`; dev hot‑reload via `watchdog`
- Read‑only helpers: `notion_test.py`, `notion_search.py`, `notion_page_inspect.py`, `notion_db_preview.py`
- Write‑restricted helpers (require `NOTION_ALLOW_WRITE=true`): `notion_update_milestones.py`, `notion_append_schema.py`, `notion_create_milestone_db.py`

Excel Viewer (`projects/excel`)
- Flask app served by Gunicorn
- Multi‑file upload; multi‑sheet selection; tabbed viewing (Excel-style A/B/C and row markers, selectable individually or with Ctrl for multi-select)
- Inline table cell editing (client‑side) and export to `.xlsx`
- i18n (English/Vietnamese) with ENG/VIE switch (top‑right)
- Env‑driven config and temp uploads auto‑cleanup
- Per‑column filters via dropdown (▾): searchable multi‑select of unique values; supports blanks; multiple filters at once
- Large tables scroll within the panel; NaN values render as blanks
- Upload page includes per-file “Select all sheets”/“Clear” controls for faster setup, and Selected Sheets includes a Home button to jump back to the landing page

Env vars (Excel Viewer)
- `PORT` (default 8000)
- `MAX_UPLOAD_MB` (default 16)
- `UPLOAD_TTL_HOURS` (default 24)
- `FLASK_SECRET_KEY` (default `dev` – set in production)

Dev loop (Excel Viewer)
- `cd projects/excel && docker compose up -d dev` for auto‑reload on changes
- Rebuild only after dependency changes: `docker compose build dev && docker compose up -d dev`

## Developer Docs
- Workspace: `docs/DEV_GUIDE.md`
- Notion: `projects/notion/DEV_GUIDE.md`
- Excel Viewer: `projects/excel/README.md` and `projects/excel/DEV_GUIDE.md`

## Notion Setup (one‑time)
1. Notion → Settings & members → Connections → Develop your own integrations → New integration
2. Copy the Internal Integration Token
3. Share the target page/database with the integration (open page → Share → Invite integration)

## Environment Files (.env vs .env.example)
- `.env.example` documents required variables (safe to commit)
- `.env` holds real secrets (git‑ignored); loaded by Compose

Common Issues
- 404/“object not found”: page/database not shared with the integration
- Missing token: ensure `.env` contains `NOTION_TOKEN`
- Docker engine not running: start Docker Desktop and verify `docker info`
