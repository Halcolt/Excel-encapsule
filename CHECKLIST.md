# Workspace Checklist (Multi-Project)

Use this list to track requirements and tasks across subprojects. Mark items with `[x]` when done. Add owners and notes inline.

## Workspace Layout
- [x] Create `projects/` folder
- [x] Add Notion subproject at `projects/notion`
- [x] Add Excel Viewer subproject at `projects/excel`

## Docker Images (per subproject)
- Notion: [x] build OK from `projects/notion`
- Excel Viewer: [x] image builds and runs from `projects/excel`
- UI (optional): [ ] scaffold image [ ] build OK

## Environment Management
- Root: [x] README documents env usage and per‑subproject config
- Notion subproject: [x] `.env.example` present with `NOTION_TOKEN`, `NOTION_PAGE_ID`, `NOTION_ALLOW_WRITE`
- Excel Viewer: [x] envs via compose (`PORT`, `MAX_UPLOAD_MB`, `UPLOAD_TTL_HOURS`)

## Notion Subproject (projects/notion)
- Access: [x] Token configured [x] Page shared [x] Auth test OK
- Safety: [x] Write‑protection via `NOTION_ALLOW_WRITE`
- Milestones: [x] Schema drafted on page [ ] Create DB [ ] Store `MILESTONE_DB_ID` in env
- Tooling: [ ] Verify hot‑reload (`docker compose up dev`)
- Scripts: [x] Search/Inspect/Preview (read‑only) [x] Update scripts guarded (write‑restricted)

## Excel ↔ Notion Data Flow
- [ ] Define Excel column ↔ Notion property mapping
- [ ] Implement import script (Excel → Notion) with idempotent upsert
- [ ] Implement update/merge strategy (key selection, dedupe)
- [ ] Optional: Export script (Notion → Excel)

## Dev Experience
- [ ] Sample data and fixtures for tests
- [x] Logging and basic error handling (Excel Viewer)
- [ ] Rate‑limit/backoff safeguards

## Documentation
- Root README: [x] explain multi‑project layout and how to run each subproject
- Notion README: [x] quick start and write‑protection notes
- Excel README/DEV_GUIDE: [x] present and linked

## Security & Secrets
- [x] `.env` ignored by git (root and subfolders)
- [x] Enforce Notion write‑protection via `NOTION_ALLOW_WRITE`
- [ ] Document token rotation and per‑env tokens (dev/prod)

## Excel Viewer Feature Checklist
- [x] Multi‑file upload
- [x] Multi‑sheet selection (across files)
- [x] Tabbed viewing
- [x] Inline editing (client-side)
- [x] Export selected sheets to `.xlsx`
- [x] i18n ENG/VIE + pill switch
- [x] Env-driven config (size/port/TTL)
- [x] Gunicorn entry in Docker
- [x] Temp uploads TTL cleanup
- [x] Per‑column filters (dropdown ▾, searchable, multi‑select, blanks)
- [x] Scrollable table container to prevent overflow
- [x] Normalize NaN to blank in rendered tables
