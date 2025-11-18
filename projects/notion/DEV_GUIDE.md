# Notion Subproject – Developer Guide

This subproject provides a Dockerized Python toolkit for interacting with Notion for documentation and project management. By default it is read-only, with explicit guards for any write operation.

## Runbook
- Copy env: `Copy-Item .env.example .env` (or rely on repo root `.env`).
- Required env vars:
  - `NOTION_TOKEN` — internal integration token (share the page with the integration in Notion).
  - `NOTION_PAGE_ID` — optional default page id to target (UUID-like; from the page URL).
  - `NOTION_ALLOW_WRITE` — default `false`. Set to `true` only for intentional writes.
- Build: `docker compose build`
- Auth test: `docker compose run --rm app python notion_test.py`
- Search: `docker compose run --rm app python notion_search.py "Excel Encapsule"`
- Inspect page blocks: `docker compose run --rm app python notion_page_inspect.py <page_id>`
- Preview database: `docker compose run --rm app python notion_db_preview.py <database_id> 10`
- Dev loop (auto-restart): `docker compose up dev`

## Code Map
- `app/notion_util.py`
  - `require_write_access()` — exits unless `NOTION_ALLOW_WRITE` is `true`/`1`/`yes`.
- `app/notion_test.py`
  - Purpose: sanity check auth. Calls `users.me` via SDK.
  - Endpoint(s): `GET /v1/users/me` (SDK: `notion.users.me()`).
- `app/notion_search.py`
  - Purpose: search pages/databases by keyword.
  - Endpoint(s): `POST /v1/search` (SDK: `notion.search(query=..., page_size=...)`).
  - Output: lists object type, title, id, url, and a quick property summary for databases.
- `app/notion_page_inspect.py`
  - Purpose: list immediate child blocks for a page.
  - Endpoint(s): `GET /v1/blocks/{block_id}/children` (SDK: `blocks.children.list`).
  - Output: block id, type, and basic text for headings/paragraphs/to-dos.
- `app/notion_db_preview.py`
  - Purpose: preview a database schema and first N rows.
  - Endpoint(s): `GET /v1/databases/{id}`, `POST /v1/databases/{id}/query`.
  - Simplifies common property types for readable output.
- `app/notion_list_databases.py`
  - Purpose: quick list of accessible databases (found by search).
  - Endpoint(s): `POST /v1/search` filtered client-side to `object == "database"`.
- Write-restricted scripts (require `NOTION_ALLOW_WRITE=true`):
  - `app/notion_update_milestones.py`
    - Updates to-do blocks to checked; appends a "Notion Integration" section.
    - Endpoint(s): `GET /blocks/{id}/children`, `PATCH /blocks/{id}` (to_do), `PATCH /blocks/{id}/children` (append).
  - `app/notion_append_schema.py`
    - Appends a "Milestone Database Schema" section as bullets; marks a to-do done if present.
    - Endpoint(s): `PATCH /blocks/{id}/children` (append), `PATCH /blocks/{id}` (to_do).
  - `app/notion_create_milestone_db.py`
    - (Optional) Create a Milestones database and seed items. Currently guarded and conservative to avoid misconfiguration.
    - Endpoint(s): `POST /v1/databases`, `PATCH /v1/databases/{id}`, `POST /v1/pages`.

## Data Access
- All data reads and writes go through the official Notion API via `notion-client`.
- There is no local database in this subproject.

## Development Notes
- Write-protection: keep `NOTION_ALLOW_WRITE=false` in `.env`. Temporarily set to `true` only for a specific update command; revert afterward.
- Rate limits: Notion applies request limits; keep one-off writes small and avoid loops without delays.
- IDs: Page and Database IDs can be copied from Notion URLs (32-character hex, sometimes with dashes).

## Updating Excel Viewer Status in Notion
- A ready-to-paste status file is generated in the repo:
  - `projects/excel/STATUS_NOTION.md`
- Open that file and paste its contents into your Notion project page.
- Optional (advanced): automate with a write-restricted script once a target page/database is defined.
  - Env: `NOTION_TOKEN`, `NOTION_ALLOW_WRITE=true`, `EXCEL_STATUS_PAGE_ID=<target_page_id>`
  - Run: `docker compose run --rm app python notion_update_excel_status.py`

## Manage Tasks and Milestones (Databases)

Discover databases
- `docker compose run --rm app python notion_scan_workspace.py --query "Task Milestone"`
- Note the database IDs and property names.

Update statuses (dry-run)
- `docker compose run --rm app python notion_update_tasks_milestones.py --tasks <TASK_DB_ID> --milestones <MILESTONE_DB_ID>`

Apply updates (write-restricted)
- Set env: `NOTION_ALLOW_WRITE=true`
- Optionally set property mappings via env or CLI:
  - `TASK_STATUS_PROPERTY` (default `Status`)
  - `TASK_DONE_VALUE` (default `Done`)
  - `TASK_COMPLETED_CHECKBOX` (e.g., `Completed`)
  - `TASK_CHECKLIST_NUMERIC` (e.g., `Checklist Done %`)
- Run: `docker compose run --rm app python notion_update_tasks_milestones.py --apply --tasks <TASK_DB_ID> --milestones <MILESTONE_DB_ID>`

Enrich tasks (completion note + subtasks)
- Dry-run: `docker compose run --rm app python notion_enrich_tasks.py --db <TASK_DB_ID>`
- Apply: set `NOTION_ALLOW_WRITE=true` and run with `--apply`
- Optional mappings via env/CLI:
  - `TASK_STATUS_PROPERTY` / `TASK_DONE_VALUE`
  - `TASK_COMPLETED_CHECKBOX` or `TASK_CHECKLIST_NUMERIC`
  - `SUBTASKS_TEXT_PROPERTY` or `SUBTASKS_MULTISELECT_PROPERTY`
  - `EFFORT_NUMBER_PROPERTY` + `BIG_TASK_THRESHOLD` (e.g., 5) to auto-create placeholder subtasks when big

## Common Issues
- 401 Unauthorized: invalid token or token not present in env.
- 404 Object not found: the integration was not shared to that page/database.
- Property mismatch: creating pages in a database requires property types to exist; create/update database properties first.
