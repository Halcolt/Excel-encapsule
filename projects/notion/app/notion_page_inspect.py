"""Notion subproject script: page inspection."""
import os
import sys
from typing import Any, Dict, List
from notion_client import Client


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


def main() -> None:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("Missing NOTION_TOKEN env var. Set it in .env")
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python notion_page_inspect.py <page_id>")
    page_id = sys.argv[1]
    client = Client(auth=token)

    blocks = list_children(client, page_id)
    if not blocks:
        print("No blocks on page.")
        return
    print(f"Found {len(blocks)} block(s) on page {page_id}\n")
    for i, b in enumerate(blocks, 1):
        btype = b.get("type")
        bid = b.get("id")
        print(f"{i}. [{btype}] id={bid}")
        if btype == "heading_1":
            print("   ", b[btype].get("rich_text", [{}])[0].get("plain_text", ""))
        elif btype == "heading_2":
            print("   ", b[btype].get("rich_text", [{}])[0].get("plain_text", ""))
        elif btype == "heading_3":
            print("   ", b[btype].get("rich_text", [{}])[0].get("plain_text", ""))
        elif btype == "paragraph":
            texts = b[btype].get("rich_text", [])
            txt = "".join(t.get("plain_text", "") for t in texts)
            if txt:
                print("   ", txt)
        elif btype == "to_do":
            txt = "".join(t.get("plain_text", "") for t in b[btype].get("rich_text", []))
            checked = b[btype].get("checked")
            print(f"    - [{'x' if checked else ' '}] {txt}")
        elif btype == "bulleted_list_item":
            txt = "".join(t.get("plain_text", "") for t in b[btype].get("rich_text", []))
            print("    - ", txt)
        elif btype == "child_database":
            name = b[btype].get("title")
            print(f"   database title: {name}")
        elif btype == "child_page":
            title = b[btype].get("title")
            print(f"   child page: {title}")


if __name__ == "__main__":
    main()
