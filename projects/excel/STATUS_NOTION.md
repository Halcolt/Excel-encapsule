# Excel Viewer – Status (for Notion)

Scope
- Simple web UI for viewing/editing/exporting Excel/CSV

Current Features
- Multi‑file upload and multi‑sheet selection (across files)
- Tabbed viewing of selected sheets
- Inline table edits (client‑side)
- Export selected sheets to `.xlsx`
- i18n: English/Vietnamese with ENG/VIE pill switch
- Per‑column filters via dropdown (▾): searchable multi‑select of unique values; supports blanks; multiple filters at once
- Large tables scroll within the panel; NaN values render as blanks

Tech
- Flask served by Gunicorn; pandas/openpyxl
- Dockerized; env‑driven config (`PORT`, `MAX_UPLOAD_MB`, `UPLOAD_TTL_HOURS`, `FLASK_SECRET_KEY`)
- Temp uploads with TTL cleanup

How to Run
- `cd projects/excel && docker compose up --build`
- Open `http://localhost:8080`
 - Dev auto‑reload: `docker compose up -d dev`

Next
- CSRF tokens, drag‑drop upload, CSV encoding/delimiter detect
- App factory + Blueprints; services/ports and adapters
- Basic tests
