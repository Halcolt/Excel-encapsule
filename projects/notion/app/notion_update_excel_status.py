"""
Write-restricted helper: Update a Notion page with the Excel Viewer status.

Usage
- Ensure env:
  - NOTION_TOKEN
  - NOTION_ALLOW_WRITE=true
  - EXCEL_STATUS_PAGE_ID=<target_page_id>
- Run from projects/notion:
  docker compose run --rm app python notion_update_excel_status.py

This script reads projects/excel/STATUS_NOTION.md and replaces the target page content
with a single markdown block. Adjust as needed for your workspace structure.
"""
import os
from notion_client import Client
from notion_util import require_write_access


def main() -> None:
    require_write_access()
    token = os.environ.get("NOTION_TOKEN")
    page_id = os.environ.get("EXCEL_STATUS_PAGE_ID")
    if not token or not page_id:
        raise SystemExit("Missing NOTION_TOKEN or EXCEL_STATUS_PAGE_ID in environment")

    status_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "excel", "STATUS_NOTION.md")
    status_path = os.path.normpath(status_path)
    if not os.path.exists(status_path):
        raise SystemExit(f"Status file not found: {status_path}")

    with open(status_path, "r", encoding="utf-8") as f:
        md = f.read()

    notion = Client(auth=token)

    # Replace page children with a single markdown block
    # Notion API v2022-06-28+ supports markdown via 'paragraph' rich_text; for simplicity, put all text into one block.
    notion.blocks.children.append(
        block_id=page_id,
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": md},
                        }
                    ]
                },
            }
        ],
    )

    print("Excel Viewer status appended to page", page_id)


if __name__ == "__main__":
    main()

