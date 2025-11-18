# Notion Subproject

This subproject contains all Notion-related code. It is self-contained and runnable from this directory.

Quick start
- Ensure you have a `.env` at the repo root with `NOTION_TOKEN` (and optional `NOTION_PAGE_ID`).
- Build: `docker compose -f projects/notion/docker-compose.yml build` (or run from this folder: `docker compose build`).
- Test auth: `docker compose run --rm app python notion_test.py`
- Dev loop: `docker compose up dev`

Write protection
- By default, scripts do not modify Notion content. To allow a specific write operation, set `NOTION_ALLOW_WRITE=true` in your environment for that command only, then set it back to false.

Scripts
- Read-only: `notion_test.py`, `notion_search.py`, `notion_page_inspect.py`, `notion_db_preview.py`.
- Write-restricted: `notion_update_milestones.py`, `notion_append_schema.py`, `notion_create_milestone_db.py`.

Environment
- This compose file uses the repo root `.env` via `../../.env` so secrets are centralized.

