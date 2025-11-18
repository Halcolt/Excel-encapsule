"""Notion subproject script: append schema bullets."""
import os
from notion_client import Client
from notion_util import require_write_access

PAGE_ID = os.environ.get("NOTION_PAGE_ID", "2a26de36-3b1c-80f6-890d-d1fda7a3c1a9")


def main() -> None:
    # Enforce read-only by default
    require_write_access()
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("Missing NOTION_TOKEN env var. Set it in .env")
    client = Client(auth=token)

    schema_bullets = [
        "Name — title",
        "Status — status (Todo, In Progress, Blocked, Done)",
        "Priority — select (Low, Medium, High)",
        "Due — date",
        "Area — select (Setup, Notion, Excel, Sync, Docs)",
        "Notes — rich_text",
    ]

    children = [
        {"heading_3": {"rich_text": [{"type": "text", "text": {"content": "Milestone Database Schema"}}]}},
    ]
    for item in schema_bullets:
        children.append({
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": item}}]
            }
        })

    client.blocks.children.append(block_id=PAGE_ID, children=children)

    # Best-effort: mark the related task as done if present
    # Iterate immediate children, find to_do with exact text.
    start_cursor = None
    while True:
        resp = client.blocks.children.list(block_id=PAGE_ID, start_cursor=start_cursor)
        for b in resp.get("results", []):
            if b.get("type") == "to_do":
                txt = "".join(t.get("plain_text", "") for t in b["to_do"].get("rich_text", []))
                if txt.strip() == "Decide milestone database schema" and not b["to_do"].get("checked"):
                    client.blocks.update(block_id=b["id"], to_do={"checked": True})
        if not resp.get("has_more"):
            break
        start_cursor = resp.get("next_cursor")

    print("Appended schema section and marked task done (if found).")


if __name__ == "__main__":
    main()
