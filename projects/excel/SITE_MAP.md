# Excel Viewer – Site Map & Flow

Purpose
- Show the site flow, which template each view uses, the onAction events, and where navigation goes next. Notes also cover new UX controls (select-all sheets, Home shortcut, Ctrl multi-select).

High-Level Flow

  ┌───────────────┐          POST /upload            ┌─────────────────┐
  │ GET /         │ ───────────────────────────────► │ GET /select/{t} │
  │ index.html    │                                  │ select.html      │
  └──────┬────────┘                                  └─────────┬───────┘
         │                                                      │
         │                                                      │ POST /render_multi
         │                                                      ▼
         │                                            ┌────────────────────┐
         │                                            │ multi_view.html     │
         │                                            │ (tabs, filters,     │
         │                                            │  row/col select)    │
         │                                            └─────────┬──────────┘
         │                                                      │
         │                         POST /export (download .xlsx)│
         │                                                      ▼
         │                                            ┌────────────────────┐
         │                                            │ File download       │
         │                                            │ export.xlsx         │
         │                                            └────────────────────┘
         │
         └─ Optional single view path:
            POST /render  ─────────────►  GET view.html (single sheet)

Language switch (any page): GET /set-lang/{lang}?next=<safe-url>

Routes ▸ Handlers ▸ Templates
- GET / ▸ index() ▸ 	emplates/index.html
  - Client-side file staging, watchdog upload UX
- POST /upload ▸ upload_files() ▸ 302 to /select/{token}
- GET /select/{token} ▸ select() ▸ 	emplates/select.html
- POST /render_multi ▸ ender_multi() ▸ 	emplates/multi_view.html
- POST /render ▸ ender_view() ▸ 	emplates/view.html
- POST /export ▸ export_excel() ▸ stream .xlsx
- GET /set-lang/{lang} ▸ set_lang_route() ▸ safe redirect (index/select)

Pages ▸ onAction
- index.html
  - onAddFiles: open OS picker, stage files (JS)
  - onClearAll: remove staged files (JS)
  - onContinue: POST /upload (FormData) → redirect to /select/{token}
- select.html
  - onFileSelectAll: click “Select all sheets” (per file) to check every sheet in that file
  - onFileClear: clear selections for that file only
  - onPickSheets: toggle specific sheet checkboxes
  - onOpen: POST /render_multi
  - onBack: GET /
  - onSetLang: GET /set-lang/{lang}?next=/select/{token}
- multi_view.html
  - onTabClick: switch active sheet panel (JS)
  - onIncludeToggle: include/exclude a tab from export
  - onEditCell: contentEditable updates in place (client-only)
  - onFilterOpen: click ▾ to open searchable multi-select dropdown
  - onFilterApply/Clear: cache filters client-side, re-evaluate rows
  - onRowMarkerClick: select/deselect rows; Ctrl/Cmd adds to selection; readout updates text boxes
  - onColMarkerClick: select/deselect columns; Ctrl/Cmd adds to selection
  - onHome: jump back to index.html
  - onExportSelected: POST /export with [{name, headers, rows}] → download .xlsx
  - onSetLang: GET /set-lang/{lang}?next=/select/{token}
- iew.html
  - Same controls as a single panel in multi_view.html (Home button, filters, Ctrl multi-select)

Data Lifecycle
- Uploads stored per-token under UPLOAD_ROOT/{token} (auto-cleaned by TTL thread)
- Selection page only inspects metadata (file list + sheet names)
- Render step loads DataFrame, illna(""), renders HTML table (no state persisted server-side)
- Edits, filters, selections live only in the browser until export
- Export posts the edited tables → server writes .xlsx in-memory

Internationalization
- JSON translations in pp/i18n; 	(key) injected server-side
- Language switch stores preference in session; only redirects to GET views (index/select)

File ↔ Template Map
- 	emplates/index.html – upload UX with add/remove file staging
- 	emplates/select.html – file cards + per-file select-all/clear controls
- 	emplates/multi_view.html – main workspace (tabs, filters, Home, row/col selection)
- 	emplates/view.html – single-sheet inspect/edit (optional path)

Suggested Next Steps
1. Shareable deep-link view route (e.g., /v/{token}?files=...) so language switch refreshes the current state without re-uploading.
2. Persist edits/filters server-side (signed JSON or Redis) so reloading keeps changes.
3. Bulk actions: delete/insert rows, column sort, find & replace (row/column selection groundwork already in place).
4. Add CSRF protection, MIME validation, and async export for very large sheets.
