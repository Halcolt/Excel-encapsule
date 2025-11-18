# Developer Guide

This repository is a multi‑project workspace. Each subproject is self‑contained (Dockerized) and can be developed independently.

## Goals
- Keep tools simple for non‑Excel users (view, light edit, export)
- Clean architecture to avoid tech debt; deployment‑ready
- Use Notion for docs/PM only (guard writes)

## Layout
- `projects/notion/` – Notion tooling (documentation/PM helpers only)
- `projects/excel/` – Excel Viewer web app
- Future examples: `projects/ui/`, `projects/excel-service/`

## Environments & Secrets
- Root `.env` (ignored by git) can hold shared values used by subprojects.
- Every subproject may also have its own `.env` and `docker-compose.yml` with envs.
- Never commit real tokens or secrets; only templates belong in VCS.

## Docker Basics (per subproject)
- Build: `docker compose build`
- One‑off run: `docker compose run --rm app <command>`
- Dev loop: `docker compose up dev` (when configured)

## Notion Write‑Protection Policy
- The repo treats Notion as docs/PM only. All write scripts are gated by `NOTION_ALLOW_WRITE`.
- Enable writes only intentionally: set `NOTION_ALLOW_WRITE=true` for a single command, then revert.

## Excel Viewer Architecture (overview)
- App: Flask served by Gunicorn
- Features: multi‑file upload, multi‑sheet selection, tabbed view, inline edits, export to `.xlsx`
- i18n: JSON translations, ENG/VIE switch via `/set-lang/<lang>`
- Config: `PORT`, `MAX_UPLOAD_MB`, `UPLOAD_TTL_HOURS`, `FLASK_SECRET_KEY`
- Temp uploads: stored under system temp; background TTL cleanup thread removes old sessions
- Filters: column‑level dropdowns (▾) with searchable, multi‑select value lists; blanks supported; combined filters
- UI: tables wrapped in a scrollable container to prevent overflow; NaN renders as blank

Dev loop
- `cd projects/excel && docker compose up -d dev` (Gunicorn `--reload`)

Future refactor steps
- App factory + Blueprints
- Services/ports (storage/parser/export) with adapters
- CSRF tokens, auth, and drag‑drop uploads

## How To Add a New Subproject
1. Create `projects/<name>/` with `Dockerfile`, `docker-compose.yml`, `.env.example`, and a `README.md`.
2. Put Python code under `projects/<name>/app` and mount it in the compose file.
3. Add a checklist in `projects/<name>/CHECKLIST.md`.
4. Update the root `CHECKLIST.md` with status for the new subproject.

## References
- Notion subproject: `projects/notion/DEV_GUIDE.md`
- Excel Viewer subproject: `projects/excel/DEV_GUIDE.md`
