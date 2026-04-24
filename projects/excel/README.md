# Excel Viewer (Dockerized)

Minimal web app to open Excel (`.xlsx`) or CSV files, select multiple sheets across files, view them in tabs, make light in-browser edits, and export to `.xlsx`.

## Run

1. Open a terminal in `projects/excel`
2. Build and start:
   - Docker Compose v2: `docker compose up --build`
   - Docker Compose v1: `docker-compose up --build`
3. Open `http://localhost:8080`

## Notes
- Multi-file upload and multi-sheet selection across files
- Tabbed sheet view with Excel-style row/column markers and Ctrl/Cmd multi-select
- Inline edits are client-side in the browser table
- Export writes a new `.xlsx` workbook from the current browser state
- Column format presets are still in progress: export can coerce values into target Excel formats, but the browser table does not live-preview number/date format changes yet
- Per-column filters support searchable multi-select values, including blanks
- Row/column cleanup tools can delete selected rows, columns, or rows with blank values in selected columns
- Tables stay inside a scrollable panel
- ENG/VIE language switch is available in the UI
- Max upload size defaults to 16 MB
- Supported file types: `.xlsx`, `.csv`

## Environment
- `PORT` default `8000`
- `MAX_UPLOAD_MB` default `16`
- `UPLOAD_TTL_HOURS` default `24`
- `FLASK_SECRET_KEY` default `dev` and must be set explicitly outside local development

## Dev Mode
- `docker compose up -d dev`
- Changes under `app/` trigger reload
- Rebuild after dependency changes: `docker compose build dev && docker compose up -d dev`

## Tests
- Local Python: `pytest projects/excel/tests -q`
- Docker: `docker compose run --rm app pytest tests -q`
