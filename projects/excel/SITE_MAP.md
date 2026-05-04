# Excel Viewer Site Map

## High-Level Flow

1. `GET /` -> upload files
2. `POST /upload` -> tokenized temp storage
3. `GET /select/<token>` -> choose sheets
4. `POST /render_multi` -> main workspace (`multi_view.html`)
5. `POST /export` -> download `.xlsx`

Language switch:
- `GET /set-lang/<lang>?next=<safe_get_url>`

## Workspace Layout (`multi_view.html`)

- Left sidebar:
  - `General`: selection info, color tools
  - `Advanced`: destructive actions + Mapping Compare entry
- Header actions:
  - Show filters
  - Undo
  - Find & Replace
  - Export
  - ENG/VIE switch
- Body:
  - Tab per selected sheet
  - Editable table with filters, row/column markers, cell selection

## Modal Surfaces

- Export modal:
  - Select tabs to export
- Find & Replace modal:
  - Find next / replace / replace all
  - Draggable panel
- Mapping Compare modal:
  - Pick left and right sheets
  - Build left/right column mappings
  - Mark key columns
  - Run compare
  - Mapping rows area has its own scroll box

## Mapping Compare Logic (Current)

1. Validate selected sheets and mapping rows
2. Require at least one KEY mapping
3. Remove rows with empty KEY values
4. Build key buckets on both sheets
5. Compare matched pairs and color cells
6. Color missing-side records by row
7. Mark internal duplicate keys with dedicated key color
8. Reinitialize table enhancements and keep undo snapshot

Color semantics:
- KEY match: blue
- Value match: green
- Value diff: red
- Missing counterpart row: orange
- Duplicate key (same sheet): purple
