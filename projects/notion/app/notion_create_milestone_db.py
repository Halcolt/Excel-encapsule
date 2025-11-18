"""Notion subproject script: create milestone DB."""
import os
from typing import Any, Dict, List
from notion_client import Client
from notion_util import require_write_access

DEFAULT_PAGE_ID = "2a26de36-3b1c-80f6-890d-d1fda7a3c1a9"


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


def find_existing_db_id(client: Client, page_id: str, title: str) -> str | None:
    for b in list_children(client, page_id):
        if b.get("type") == "child_database":
            if b["child_database"].get("title", "") == title:
                return b.get("id")
    return None


def ensure_milestone_db(client: Client, page_id: str) -> str:
    title = "Milestones"
    existing = find_existing_db_id(client, page_id, title)
    if existing:
        return existing

    db = client.databases.create(
        parent={"type": "page_id", "page_id": page_id},
        title=[{"type": "text", "text": {"content": title}}],
        properties={
            "Name": {"title": {}},
            "Status": {
                "status": {
                    "options": [
                        {"name": "Todo", "color": "default"},
                        {"name": "In Progress", "color": "blue"},
                        {"name": "Blocked", "color": "red"},
                        {"name": "Done", "color": "green"},
                    ]
                }
            },
            "Priority": {"select": {"options": [
                {"name": "Low", "color": "gray"},
                {"name": "Medium", "color": "yellow"},
                {"name": "High", "color": "orange"},
            ]}},
            "Due": {"date": {}},
            "Area": {"select": {"options": [
                {"name": "Setup", "color": "blue"},
                {"name": "Notion", "color": "purple"},
                {"name": "Excel", "color": "brown"},
                {"name": "Sync", "color": "pink"},
                {"name": "Docs", "color": "green"},
            ]}},
            "Notes": {"rich_text": {}},
        },
    )
    return db["id"]


def get_title_prop_name(meta: Dict[str, Any]) -> str:
    for key, val in meta.get("properties", {}).items():
        if val.get("type") == "title":
            return key
    return "Name"


def ensure_properties(client: Client, db_id: str) -> Dict[str, Any]:
    meta = client.databases.retrieve(db_id)
    props = meta.get("properties", {})
    to_add: Dict[str, Any] = {}
    if "Status" not in props:
        to_add["Status"] = {
            "status": {
                "options": [
                    {"name": "Todo", "color": "default"},
                    {"name": "In Progress", "color": "blue"},
                    {"name": "Blocked", "color": "red"},
                    {"name": "Done", "color": "green"},
                ]
            }
        }
    if "Priority" not in props:
        to_add["Priority"] = {"select": {"options": [
            {"name": "Low", "color": "gray"},
            {"name": "Medium", "color": "yellow"},
            {"name": "High", "color": "orange"},
        ]}}
    if "Due" not in props:
        to_add["Due"] = {"date": {}}
    if "Area" not in props:
        to_add["Area"] = {"select": {"options": [
            {"name": "Setup", "color": "blue"},
            {"name": "Notion", "color": "purple"},
            {"name": "Excel", "color": "brown"},
            {"name": "Sync", "color": "pink"},
            {"name": "Docs", "color": "green"},
        ]}}
    if "Notes" not in props:
        to_add["Notes"] = {"rich_text": {}}

    if to_add:
        meta = client.databases.update(database_id=db_id, properties=to_add)
    return meta


def create_row(client: Client, db_id: str, title_prop: str, name: str, status: str = "Todo", area: str | None = None, priority: str | None = None, notes: str | None = None) -> None:
    props: Dict[str, Any] = {
        title_prop: {"title": [{"text": {"content": name}}]},
    }
    # Populate optional properties if they exist
    if status:
        props["Status"] = {"status": {"name": status}}
    if area:
        props["Area"] = {"select": {"name": area}}
    if priority:
        props["Priority"] = {"select": {"name": priority}}
    if notes:
        props["Notes"] = {"rich_text": [{"text": {"content": notes}}]}

    client.pages.create(parent={"database_id": db_id}, properties=props)


def mark_todo_done(client: Client, page_id: str, text: str) -> bool:
    for b in list_children(client, page_id):
        if b.get("type") != "to_do":
            continue
        rich = b["to_do"].get("rich_text", [])
        content = "".join(t.get("plain_text", "") for t in rich).strip()
        if content == text and not b["to_do"].get("checked"):
            client.blocks.update(block_id=b["id"], to_do={"checked": True})
            return True
    return False


def append_note(client: Client, page_id: str, text: str) -> None:
    client.blocks.children.append(
        block_id=page_id,
        children=[
            {
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": text}}
                    ]
                }
            }
        ],
    )


def main() -> None:
    # Enforce read-only by default
    require_write_access()
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("Missing NOTION_TOKEN env var. Set it in .env")
    page_id = os.environ.get("NOTION_PAGE_ID", DEFAULT_PAGE_ID)

    client = Client(auth=token)

    db_id = ensure_milestone_db(client, page_id)
    meta = ensure_properties(client, db_id)
    title_prop = get_title_prop_name(meta)
    print("DB title prop:", title_prop)
    print("DB properties:", ", ".join(meta.get("properties", {}).keys()))

    # Seed core items (idempotent-ish: simple names, duplicates are acceptable for first pass)
    seed = [
        ("Dockerized Python scaffold", "Done", "Setup", "High"),
        ("Notion auth verified", "Done", "Notion", "Medium"),
        ("Define Excel task catalog", "Todo", "Excel", "Medium"),
        ("Excel parsing utilities", "Todo", "Excel", "High"),
        ("Excel → Notion import", "Todo", "Sync", "High"),
        ("Notion → Excel export (optional)", "Todo", "Sync", "Low"),
    ]
    for name, status, area, prio in seed:
        create_row(client, db_id, title_prop, name=name, status=status, area=area, priority=prio)

    # Mark corresponding Notion page task as done
    _ = mark_todo_done(client, page_id, "Decide milestone database schema")

    append_note(client, page_id, f"Milestone database ready: {db_id}")

    # Print and optionally write env hints
    print(f"MILESTONE_DB_ID={db_id}")


if __name__ == "__main__":
    main()
