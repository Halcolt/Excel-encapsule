# Excel Viewer (Dockerized)

Web app to open Excel/CSV files, edit directly in-browser, compare sheets by mapping, and export to `.xlsx`.

## Run

1. Open terminal at `projects/excel`
2. Start dev service (recommended):
   - `docker compose up -d --build dev`
3. Open `http://localhost:8080`

Note:
- `docker-compose.yml` currently maps both `dev` and `excel-viewer` to port `8080`.
- Run only one of them at a time to avoid port conflict.

## Current Feature Set

- Multi-file upload (`.xlsx`, `.csv`)
- Multi-sheet selection across files
- Tab workspace with inline editing
- Row/column/cell selection (Ctrl/Cmd multi-select + drag cell selection)
- Column resize (drag header divider)
- Per-column filter dropdown (search + select all + blanks)
- Find & Replace draggable popup
- Undo for table structure edits (delete row/column)
- Fill color + text color palettes (Excel-like quick palette + more colors)
- Export selected tabs to `.xlsx`
- i18n ENG/VIE switch
- Advanced tool: Mapping Compare (popup workflow)

## Mapping Compare (Advanced)

Open `Advanced` -> `Open Compare Setup`.

Flow:
1. Choose left sheet and right sheet
2. Add mapping rows: left column <-> right column
3. Mark one or more mapping rows as `KEY`
4. Run compare

Color rules (based on VBA logic):
- KEY matched cell: blue
- Non-key equal value: green
- Non-key different value: red
- Record only on one side: full row orange
- Duplicate KEY inside same sheet: KEY cell purple (still compares across sheets)

Behavior notes:
- Rows with empty KEY are removed before compare (same as VBA behavior).
- Duplicate keys are not overwritten. They are bucketed and compared in appearance order.

## Environment

- `PORT` (default `8000`)
- `MAX_UPLOAD_MB` (default `16`)
- `UPLOAD_TTL_HOURS` (default `24`)
- `FLASK_SECRET_KEY` (default `dev`, set a real value in production)

## Dev Notes

- Auto reload is handled by the `dev` service.
- Rebuild only when dependencies change:
  - `docker compose build dev && docker compose up -d dev`
