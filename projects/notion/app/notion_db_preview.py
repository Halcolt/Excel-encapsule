"""Notion subproject script: database preview."""
import os
import sys
from typing import Any, Dict
from notion_client import Client


def simplify_property(value: Dict[str, Any]) -> str:
    t = value.get("type")
    v = value.get(t)
    if t == "title":
        return "".join(x.get("plain_text", "") for x in v)
    if t == "rich_text":
        return "".join(x.get("plain_text", "") for x in v)
    if t == "select":
        return (v or {}).get("name", "") if v else ""
    if t == "multi_select":
        return ", ".join(x.get("name", "") for x in (v or []))
    if t == "people":
        return ", ".join(p.get("name", "") for p in (v or []))
    if t == "checkbox":
        return str(bool(v))
    if t == "number":
        return str(v)
    if t == "date":
        return (v or {}).get("start", "")
    if t == "status":
        return (v or {}).get("name", "") if v else ""
    if t == "url":
        return v or ""
    if t == "email":
        return v or ""
    if t == "phone_number":
        return v or ""
    return t or "unknown"


def main() -> None:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("Missing NOTION_TOKEN env var. Set it in .env")

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python notion_db_preview.py <database_id> [limit]")
    database_id = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    client = Client(auth=token)
    meta = client.databases.retrieve(database_id)
    db_title = "".join(t.get("plain_text", "") for t in meta.get("title", []))
    print(f"Database: {db_title} ({database_id})")

    props = meta.get("properties", {})
    keys = list(props.keys())
    print("Properties:", ", ".join(f"{k}:{props[k]['type']}" for k in keys))

    res = client.databases.query(database_id=database_id, page_size=limit)
    rows = res.get("results", [])
    print(f"\n{len(rows)} row(s) preview:\n")
    for idx, page in enumerate(rows, 1):
        pid = page.get("id")
        pprops = page.get("properties", {})
        summary = {k: simplify_property(pprops.get(k, {})) for k in keys}
        print(f"{idx}. {pid}")
        print("   " + "; ".join(f"{k}={v}" for k, v in summary.items()))


if __name__ == "__main__":
    main()
