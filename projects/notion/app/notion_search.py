"""Notion subproject script: search helper."""
import os
import sys
from typing import Any, Dict
from notion_client import Client


def title_from(obj: Dict[str, Any]) -> str:
    # Try to resolve a display title for pages or databases
    if obj.get("object") == "database":
        title = obj.get("title", [])
        if title and isinstance(title, list):
            return "".join(t.get("plain_text", "") for t in title)
        return "(untitled database)"
    if obj.get("object") == "page":
        props = obj.get("properties", {})
        # Find the title property
        for p in props.values():
            if p.get("type") == "title":
                return "".join(t.get("plain_text", "") for t in p.get("title", [])) or "(untitled page)"
        return "(untitled page)"
    return "(unknown)"


def main() -> None:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("Missing NOTION_TOKEN env var. Set it in .env")

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else os.environ.get("NOTION_SEARCH", "excel encapsule")
    client = Client(auth=token)

    if not query or not query.strip():
        res = client.search(page_size=10)
    else:
        res = client.search(query=query, page_size=10)

    results = res.get("results", [])
    if not results:
        print(f"No results for: {query}")
        return

    print(f"Found {len(results)} result(s) for: {query}\n")
    for i, r in enumerate(results, 1):
        obj = r.get("object")
        rid = r.get("id")
        t = title_from(r)
        url = r.get("url") or r.get("public_url") or ""
        print(f"{i}. [{obj}] {t}")
        print(f"   id: {rid}")
        if url:
            print(f"   url: {url}")
        # If it's a database, show basic property names/types
        if obj == "database":
            props = r.get("properties", {})
            if props:
                pairs = ", ".join(f"{k}:{v.get('type')}" for k, v in list(props.items())[:6])
                print(f"   properties: {pairs}")
        print()


if __name__ == "__main__":
    main()
