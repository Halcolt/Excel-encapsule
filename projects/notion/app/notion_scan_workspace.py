"""
Scan Notion for likely Task/Milestone databases and print schema and sample rows.

Usage (from projects/notion):
  docker compose run --rm app python notion_scan_workspace.py --query Task

Env:
  NOTION_TOKEN (required)
"""
import os
import argparse
from typing import Any, Dict
from notion_client import Client


def prop_shape(p: Dict[str, Any]) -> str:
    t = p.get("type")
    if t == "select":
        opts = [o.get("name") for o in p.get("select", {}).get("options", [])]
        return f"select({', '.join(opts)})"
    if t == "status":
        sts = [o.get("name") for g in p.get("status", {}).get("groups", []) for o in g.get("options", [])]
        return f"status({', '.join(sts)})"
    if t == "multi_select":
        opts = [o.get("name") for o in p.get("multi_select", {}).get("options", [])]
        return f"multi_select({', '.join(opts)})"
    return t or "unknown"


def page_title(db: Dict[str, Any]) -> str:
    title_prop = db.get("title", [])
    if title_prop:
        return "".join([r.get("plain_text", "") for r in title_prop])
    return db.get("id", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="task milestone", help="Search terms (space-separated)")
    ap.add_argument("--limit", type=int, default=5, help="Sample rows per database")
    args = ap.parse_args()

    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("NOTION_TOKEN is required")

    client = Client(auth=token)
    terms = args.query.split()
    seen = set()
    print("== Databases matching query ==")
    for term in terms:
        res = client.search(query=term, page_size=50, filter={"property": "object", "value": "database"})
        for db in res.get("results", []):
            if db["id"] in seen:
                continue
            seen.add(db["id"])
            title = page_title(db)
            print(f"\nDatabase: {title} ({db['id']})")
            # Schema
            props = db.get("properties", {})
            for name, prop in props.items():
                print(f"  - {name}: {prop_shape(prop)}")
            # Sample rows
            try:
                q = client.databases.query(database_id=db["id"], page_size=args.limit)
                pages = q.get("results", [])
                for p in pages:
                    title_text = ""
                    for k, v in p.get("properties", {}).items():
                        if v.get("type") == "title":
                            title_text = "".join(rt.get("plain_text", "") for rt in v.get("title", []))
                            break
                    print(f"    • {title_text or p['id']}")
            except Exception:
                pass


if __name__ == "__main__":
    main()

