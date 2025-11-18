# Excel Viewer (Dockerized)

Minimal web app to open Excel (.xlsx) or CSV files, select multiple sheets across files, view in tabs, edit cells, and export to `.xlsx`.

## Run

1. Open a terminal in this folder: `projects/excel`
2. Build and start:

   - Docker Compose v2: `docker compose up --build`
   - Docker Compose v1: `docker-compose up --build`

3. Open `http://localhost:8080` and select one or more `.xlsx` or `.csv` files; then choose one or more sheets across files to view simultaneously. Edit cells inline and export the selected tabs to an Excel file.

Notes
- Multi-file upload; multi-sheet selection; tabbed view (Excel-style headers A/B/C and selectable rows/columns with Ctrl multi-select and selection readouts)
- Inline edits (client-side) and export selected sheets to `.xlsx`
- Per-column filters: click the small ? button in a header to open a searchable, multi-select list of values (supports blank values); multiple columns can be filtered at once
- Row/column cleanup tools: select row or column markers (Ctrl/Cmd for multi-select) then click Delete; use **Delete rows with blank data** to drop rows where the highlighted columns are empty, and use the color picker to paint entire rows, columns, or individual cells
- Large tables scroll within the panel (no overflow) and a Home button is always visible to jump back to the landing page
- Upload screen includes per-file “Select all sheets” / “Clear” controls for faster setup, and NaN values render as blanks
- i18n switch (ENG/VIE) at the top-right
- Max upload size defaults to 16 MB (configurable)
- Supported: `.xlsx`, `.csv`

Environment
- `PORT` (default 8000)
- `MAX_UPLOAD_MB` (default 16)
- `UPLOAD_TTL_HOURS` (default 24)
- `FLASK_SECRET_KEY` (default `dev` â€“ set in production)

Dev Mode (auto-reload)
- Use the `dev` service to auto-reload on code/template changes:
  - From `projects/excel`: `docker compose up -d dev`
  - Edits under `app/` trigger Gunicorn `--reload` and refresh the app
  - For dependency changes (`requirements.txt`), rebuild: `docker compose build dev && docker compose up -d dev`

