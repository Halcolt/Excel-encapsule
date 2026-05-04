# Excel Viewer Developer Guide

## Purpose

This project provides a browser-based Excel/CSV workspace for:
- quick review
- inline edits
- sheet comparison by mapping
- export back to `.xlsx`

## Stack

- Flask + Gunicorn
- pandas + openpyxl
- Server-rendered HTML templates (`app/templates`)
- Plain JavaScript on the client

## Run

From `projects/excel`:

1. Development (auto reload):
   - `docker compose up -d --build dev`
2. Production-like service:
   - `docker compose up -d --build excel-viewer`

Open: `http://localhost:8080`

Important:
- `dev` and `excel-viewer` both map host port `8080` in current compose file.
- Start only one service at a time.

## Main Routes

- `GET /` -> Upload page
- `POST /upload` -> Save files by token
- `GET /select/<token>` -> Select sheets across files
- `POST /render_multi` -> Main tabbed workspace
- `POST /render` -> Single-sheet view (legacy/optional)
- `POST /export` -> Build and download `.xlsx`
- `GET /set-lang/<lang>` -> Language switch

## Key Features

### Editing workspace
- Tab per sheet
- Inline cell editing
- Row/column marker selection
- Multi-cell drag selection
- Column resizing
- Find & Replace draggable popup
- Undo for destructive structure edits

### Filtering
- Per-column dropdown filter panel
- Search in unique values
- Select all / clear subsets
- Blank-value support

### Colors
- Fill color and text color tools
- Excel-like quick palette + advanced picker

### Advanced: Mapping Compare
- Open from sidebar `Advanced`
- Select left and right sheets
- Define mapping pairs (left column <-> right column)
- Mark one or more rows as KEY
- Run compare with VBA-aligned color rules

Color outputs:
- KEY matched: blue
- Non-key equal: green
- Non-key different: red
- Missing row on opposite side: orange
- Internal duplicate KEY: purple (still participates in compare)

## Data Handling Notes

- Uploaded files live in tokenized temp folders
- Expired folders are cleaned by a background TTL loop
- Export is built in-memory then streamed to user
- Sheet names are sanitized and deduplicated before writing

## Security/Robustness Status

- CSRF protection: enabled for POST routes
- CSV parser: encoding and delimiter detection enabled
- i18n: EN/VI JSON locale files

## Known Next Steps

- App factory + blueprints refactor
- Parser/export/storage service split
- Automated tests for compare/filter/export flows
