# Excel Viewer Checklist

## Core

- [x] Dockerized Flask app
- [x] Multi-file upload
- [x] Multi-sheet selection
- [x] Tabbed workspace
- [x] Inline cell edit
- [x] Export selected sheets to `.xlsx`
- [x] ENG/VIE language switch
- [x] Temp upload cleanup by TTL

## Table UX

- [x] Row/column markers
- [x] Ctrl/Cmd multi-select rows and columns
- [x] Drag-select multiple cells
- [x] Column resize by drag
- [x] Per-column filters (search + select all + blanks)
- [x] Find & Replace popup (draggable)
- [x] Undo for row/column deletion
- [x] Fill color and text color palettes (quick + advanced)

## Advanced

- [x] Mapping Compare popup
- [x] Select left/right sheets in modal
- [x] Column mapping rows with KEY checkbox
- [x] Compare colorization aligned with VBA behavior
- [x] Handle duplicate KEY without overwrite
- [x] Highlight duplicate KEY in same sheet with separate color

## Platform / Safety

- [x] CSRF validation for POST routes
- [x] CSV smart parsing (encoding + delimiter sniff)
- [ ] App factory + blueprints refactor
- [ ] Service layer split (parser/export/storage)
- [ ] Automated route/unit tests
