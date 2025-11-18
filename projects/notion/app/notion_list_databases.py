"""Notion subproject script: list databases."""
import os
from notion_client import Client


def main() -> None:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("Missing NOTION_TOKEN env var. Set it in .env")
    client = Client(auth=token)
    res = client.search(page_size=50)
    results = [r for r in res.get("results", []) if r.get("object") == "database"]
    print(f"Found {len(results)} database(s)")
    for i, db in enumerate(results, 1):
        title = "".join(t.get("plain_text", "") for t in db.get("title", []))
        print(f"{i}. {title} | id={db.get('id')} | props={[k for k in db.get('properties', {}).keys()]}")


if __name__ == "__main__":
    main()
