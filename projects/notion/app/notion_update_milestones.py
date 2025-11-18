"""Notion subproject script: update milestones."""
import os
from typing import Any, Dict, List
from notion_client import Client
from notion_util import require_write_access

PAGE_ID = os.environ.get("NOTION_PAGE_ID", "2a26de36-3b1c-80f6-890d-d1fda7a3c1a9")


def list_children(client: Client, block_id: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    start_cursor = None
    while True:
        resp = client.blocks.children.list(block_id=block_id, start_cursor=start_cursor)
        results.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        start_cursor = resp.get("next_cursor")
    return results


def get_todo_text(block: Dict[str, Any]) -> str:
    rich = block.get("to_do", {}).get("rich_text", [])
    return "".join(t.get("plain_text", "") for t in rich)


def mark_done(client: Client, block_id: str) -> None:
    client.blocks.update(block_id=block_id, to_do={"checked": True})


def text_block(content: str) -> Dict[str, Any]:
    return {
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": content}}]
        }
    }


def heading3(text: str) -> Dict[str, Any]:
    return {
        "heading_3": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def todo(text: str, checked: bool = False) -> Dict[str, Any]:
    return {
        "to_do": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "checked": checked,
        }
    }


def main() -> None:
    # Enforce read-only by default
    require_write_access()
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("Missing NOTION_TOKEN env var. Set it in .env")

    client = Client(auth=token)
    page_id = PAGE_ID

    # 1) Mark already-done ToDo items
    targets = {
        "Create .gitignore, requirements.txt, README.md",
        "Build → docker build .",
    }
    blocks = list_children(client, page_id)
    updated = 0
    for b in blocks:
        if b.get("type") != "to_do":
            continue
        txt = get_todo_text(b)
        if txt.strip() in targets and not b.get("to_do", {}).get("checked"):
            mark_done(client, b["id"])
            updated += 1

    # 2) Append a "Notion Integration" section with tasks
    children = [
        heading3("Notion Integration"),
        todo("Token authenticated", checked=True),
        todo("Page access granted", checked=True),
        todo("Decide milestone database schema"),
        todo("Map Excel columns → Notion properties"),
        todo("Implement Excel → Notion import"),
        todo("Optional: Notion → Excel export"),
    ]
    client.blocks.children.append(block_id=page_id, children=children)

    print(f"Updated {updated} existing to-do(s) and appended Notion Integration section.")


if __name__ == "__main__":
    main()
