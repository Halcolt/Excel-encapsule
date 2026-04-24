# Excel Viewer - Developer Guide

## Purpose
- Provide a simple web UI for viewing Excel/CSV, making light edits in the browser, and exporting to `.xlsx`

## Stack
- Flask for the web app
- Gunicorn for container serving
- pandas and openpyxl for parsing/export
- Server-rendered HTML templates with minimal client-side JavaScript

## Run
- `cd projects/excel`
- `docker compose up --build`
- Open `http://localhost:8080`

## Config
- `PORT` default `8000`
- `MAX_UPLOAD_MB` default `16`
- `UPLOAD_TTL_HOURS` default `24`
- `FLASK_SECRET_KEY` default `dev`

## Current Feature Set
- Upload multiple files
- Per-file sheet selection helpers
- Select multiple sheets across files
- Tabbed viewing with row/column selection markers
- Inline cell editing in the browser table
- Export selected sheets to a newly generated `.xlsx`
- ENG/VIE language switch
- Searchable per-column filters with blank support
- Row/column cleanup actions
- Scrollable table container
- Column format presets for export are in progress only

## Important Limitations
- The browser grid is text-first HTML, not a workbook-preserving Excel model
- Format presets currently affect export only; they do not live-preview formatted values in the browser grid
- Export builds a new workbook from the edited browser state instead of patching the original workbook
- This app should be treated as a data editor, not a VBA-preserving workbook editor

## Routes
- `GET /` upload UI
- `POST /upload` save files under a temporary token directory
- `GET /select/<token>` choose sheets across uploaded files
- `POST /render_multi` render selected sheets in tabs
- `POST /export` generate an `.xlsx` from the current browser payload
- `GET /set-lang/<lang>` switch UI language

## Internals
- Temp uploads live under `UPLOAD_ROOT` or the system temp directory
- A daemon cleanup thread removes expired token directories
- Rendering normalizes blanks with `fillna("")` and `na_rep=""`
- Excel metadata inference captures source type and original number format for export helpers
- Read-only workbook metadata scanning must stay row-streamed to avoid `openpyxl` performance regressions

## Testing
- `pytest projects/excel/tests -q`
- Current automated coverage focuses on:
  - sheet-name sanitization
  - workbook metadata extraction
  - upload/select/render/export route smoke tests
- Tests should generate small workbook fixtures in code instead of depending on the checked-in demo workbook

## Suggested Next Work
- Keep stabilizing route and export behavior with more tests before adding new spreadsheet semantics
- Revisit format-presets only after the current export contract is documented and covered by tests
- If workbook fidelity or VBA support becomes a real requirement, treat that as a separate architecture track
