"""Notion subproject script."""
import os
from notion_client import Client


def main() -> None:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("Missing NOTION_TOKEN env var. Set it in .env")

    notion = Client(auth=token)
    me = notion.users.me()
    print(me)


if __name__ == "__main__":
    main()
