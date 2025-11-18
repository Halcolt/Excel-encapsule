"""
Append a detailed checklist to a Notion page (not a database item).

By default, adds a structured "Detailed Checklist (auto)" toggle with nested
sections and to-do items suitable for Excel-related work.

Usage (from projects/notion):
  docker compose run --rm app python notion_add_checklist.py --page <PAGE_ID> --apply

Env/CLI
- NOTION_TOKEN (required)
- NOTION_ALLOW_WRITE=true (required with --apply)
- --page / NOTION_PAGE_ID: target page id
- --template: excel_milestone (default) | simple

Idempotence
- The script checks existing top-level children for a toggle with the same
  title (e.g., "Detailed Checklist (auto)") and skips creation if found.
"""
import os
import argparse
from typing import List, Dict, Any
from notion_client import Client
from notion_util import require_write_access


def template_excel_milestone() -> Dict[str, List[str]]:
    return {
        "Discovery": [
            "Confirm scope and success criteria",
            "Collect sample Excel/CSV files",
            "Identify required columns and formats",
        ],
        "Preparation": [
            "Clean sample data (types, headers)",
            "Define sheet and file naming conventions",
            "Decide export sheet names",
        ],
        "Implementation": [
            "Upload and select sheets",
            "Adjust data inline (edits)",
            "Save/export test `.xlsx`",
        ],
        "Review": [
            "Stakeholder review of sample export",
            "Fix data mismatches",
            "Freeze the mapping and rules",
        ],
        "QA": [
            "Retest with new sample files",
            "Verify i18n labels",
            "Confirm large-file limits",
        ],
        "Release": [
            "Export final `.xlsx`",
            "Share and gather feedback",
            "Document steps in Notion",
        ],
    }


def template_simple() -> Dict[str, List[str]]:
    return {
        "Plan": ["Define goal", "List tasks", "Set owners"],
        "Do": ["Execute tasks", "Track progress"],
        "Review": ["Validate outcome", "Retrospective"],
    }


def has_existing_toggle(client: Client, page_id: str, title: str) -> bool:
    try:
        children = client.blocks.children.list(block_id=page_id, page_size=50)
        for b in children.get("results", []):
            if b.get("type") == "toggle":
                rts = b.get("toggle", {}).get("rich_text", [])
                text = "".join(rt.get("plain_text", "") for rt in rts)
                if text.strip() == title:
                    return True
    except Exception:
        pass
    return False


def build_blocks(struct: Dict[str, List[str]], root_title: str) -> Dict[str, Any]:
    groups: List[Dict[str, Any]] = []
    for section, items in struct.items():
        todos = [
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": it}}],
                    "checked": False,
                },
            }
            for it in items
        ]
        groups.append(
            {
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": section}}],
                    "children": todos,
                },
            }
        )

    return {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": root_title}}],
            "children": groups,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", dest="page_id", default=os.environ.get("NOTION_PAGE_ID"))
    ap.add_argument("--template", choices=["excel_milestone", "simple"], default="excel_milestone")
    ap.add_argument("--apply", action="store_true", help="Apply changes instead of dry-run")
    args = ap.parse_args()

    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("NOTION_TOKEN is required (in your .env)")
    if not args.page_id:
        raise SystemExit("Provide --page <PAGE_ID> or NOTION_PAGE_ID in env")

    apply = bool(args.apply or os.environ.get("APPLY_CHANGES", "").lower() in {"1", "true", "yes"})
    if apply:
        require_write_access()

    client = Client(auth=token)

    root_title = "Detailed Checklist (auto)"
    if has_existing_toggle(client, args.page_id, root_title):
        print("Checklist already exists; skipping creation")
        return

    struct = template_excel_milestone() if args.template == "excel_milestone" else template_simple()
    blocks = build_blocks(struct, root_title)

    print(f"Appending checklist to page {args.page_id} using template {args.template}")
    if apply:
        client.blocks.children.append(block_id=args.page_id, children=[blocks])
        print("Done")
    else:
        print("Dry-run; pass --apply to write")


if __name__ == "__main__":
    main()

