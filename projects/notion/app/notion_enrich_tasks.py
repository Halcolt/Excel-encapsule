"""
Enrich Task pages in a Notion database:
- Optionally set Status to Done based on completion rules
- Append a completion note to the page when Done
- Create a "Subtasks (auto)" toggle with to‑do child items derived from a property

Defaults can be provided via env or CLI.

Env (or CLI overrides):
- NOTION_TOKEN (required)
- NOTION_ALLOW_WRITE=true (required with --apply)
- TASK_DB_ID (optional)
- TASK_STATUS_PROPERTY (default: Status)
- TASK_DONE_VALUE (default: Done)
- TASK_COMPLETED_CHECKBOX (optional; e.g., Completed)
- TASK_CHECKLIST_NUMERIC (optional; e.g., Checklist Done %)
- SUBTASKS_TEXT_PROPERTY (optional; rich_text/title with newline/comma separated list)
- SUBTASKS_MULTISELECT_PROPERTY (optional; names become subtasks)
- EFFORT_NUMBER_PROPERTY (optional; e.g., Effort/Points)
- BIG_TASK_THRESHOLD (default: 0) – if Effort >= threshold and no subtasks provided, create 3 placeholders

Usage (from projects/notion):
  docker compose run --rm app python notion_enrich_tasks.py --db <TASK_DB_ID> --apply
"""
import os
import argparse
from datetime import datetime
from typing import Any, Dict, List, Optional

from notion_client import Client
from notion_util import require_write_access


def get_prop(page: Dict[str, Any], name: str) -> Optional[Dict[str, Any]]:
    return page.get("properties", {}).get(name)


def status_name(page: Dict[str, Any], name: str) -> Optional[str]:
    p = get_prop(page, name)
    if not p or p.get("type") != "status":
        return None
    st = p.get("status")
    if not st:
        return None
    return st.get("name")


def checkbox_value(page: Dict[str, Any], name: str) -> Optional[bool]:
    p = get_prop(page, name)
    if not p or p.get("type") != "checkbox":
        return None
    return bool(p.get("checkbox"))


def number_value(page: Dict[str, Any], name: str) -> Optional[float]:
    p = get_prop(page, name)
    if not p or p.get("type") != "number":
        return None
    return p.get("number")


def title_of(page: Dict[str, Any]) -> str:
    for k, v in page.get("properties", {}).items():
        if v.get("type") == "title":
            return "".join(rt.get("plain_text", "") for rt in v.get("title", []))
    return page.get("id", "")


def text_property_lines(page: Dict[str, Any], name: str) -> List[str]:
    p = get_prop(page, name)
    if not p:
        return []
    data = ""
    if p.get("type") == "rich_text":
        data = "".join(rt.get("plain_text", "") for rt in p.get("rich_text", []))
    elif p.get("type") == "title":
        data = "".join(rt.get("plain_text", "") for rt in p.get("title", []))
    data = data.strip()
    if not data:
        return []
    # split on newlines or commas
    parts = [s.strip() for s in data.replace("\r", "\n").replace(",", "\n").split("\n")]
    return [s for s in parts if s]


def multiselect_names(page: Dict[str, Any], name: str) -> List[str]:
    p = get_prop(page, name)
    if not p or p.get("type") != "multi_select":
        return []
    return [o.get("name", "").strip() for o in p.get("multi_select", []) if o.get("name")]


def ensure_completion_note(client: Client, page_id: str, apply: bool) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    note_text = f"Completed ✅ {ts}"
    # Append a paragraph; simplest idempotence approach: always append with timestamp
    if apply:
        client.blocks.children.append(
            block_id=page_id,
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": note_text}}]},
                }
            ],
        )


def ensure_subtasks(client: Client, page_id: str, subtasks: List[str], apply: bool) -> None:
    if not subtasks:
        return
    children = [
        {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": s}}],
                "checked": False,
            },
        }
        for s in subtasks
    ]
    toggle = {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": "Subtasks (auto)"}}],
            "children": children,
        },
    }
    if apply:
        client.blocks.children.append(block_id=page_id, children=[toggle])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", dest="task_db", default=os.environ.get("TASK_DB_ID"))
    ap.add_argument("--task-status", default=os.environ.get("TASK_STATUS_PROPERTY", "Status"))
    ap.add_argument("--task-done", default=os.environ.get("TASK_DONE_VALUE", "Done"))
    ap.add_argument("--task-completed", dest="task_completed_checkbox",
                    default=os.environ.get("TASK_COMPLETED_CHECKBOX"))
    ap.add_argument("--task-checklist", dest="task_checklist_numeric",
                    default=os.environ.get("TASK_CHECKLIST_NUMERIC"))
    ap.add_argument("--subtasks-text", dest="subtasks_text_prop",
                    default=os.environ.get("SUBTASKS_TEXT_PROPERTY"))
    ap.add_argument("--subtasks-multi", dest="subtasks_multi_prop",
                    default=os.environ.get("SUBTASKS_MULTISELECT_PROPERTY"))
    ap.add_argument("--effort-prop", dest="effort_prop",
                    default=os.environ.get("EFFORT_NUMBER_PROPERTY"))
    ap.add_argument("--big-threshold", type=float, default=float(os.environ.get("BIG_TASK_THRESHOLD", 0) or 0))
    ap.add_argument("--apply", action="store_true", help="Apply changes instead of dry-run")
    args = ap.parse_args()

    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("NOTION_TOKEN is required (present in your .env)")
    if not args.task_db:
        raise SystemExit("Provide --db <TASK_DB_ID> or set TASK_DB_ID in env")

    apply = bool(args.apply or os.environ.get("APPLY_CHANGES", "").lower() in {"1", "true", "yes"})
    if apply:
        require_write_access()

    client = Client(auth=token)

    cursor = None
    total = 0
    updated = 0
    while True:
        kwargs = {"database_id": args.task_db, "page_size": 50}
        if cursor:
            kwargs["start_cursor"] = cursor
        q = client.databases.query(**kwargs)
        for page in q.get("results", []):
            total += 1
            title = title_of(page)
            pid = page.get("id")
            cur_status = status_name(page, args.task_status)

            # Decide completion
            should_done = False
            if args.task_completed_checkbox:
                v = checkbox_value(page, args.task_completed_checkbox)
                should_done = should_done or bool(v)
            if args.task_checklist_numeric:
                num = number_value(page, args.task_checklist_numeric)
                if num is not None:
                    should_done = should_done or (num >= 100 or num >= 1.0)

            # Build subtasks
            subtasks: List[str] = []
            if args.subtasks_text_prop:
                subtasks += text_property_lines(page, args.subtasks_text_prop)
            if args.subtasks_multi_prop:
                subtasks += multiselect_names(page, args.subtasks_multi_prop)
            if not subtasks and args.effort_prop and args.big_threshold:
                eff = number_value(page, args.effort_prop) or 0
                if eff >= args.big_threshold:
                    subtasks = ["Plan", "Do", "Review"]

            print(f"- {title} [{cur_status or '-'}]{' DONE' if should_done else ''}{' +subtasks' if subtasks else ''}")

            if should_done and cur_status != args.task_done:
                updated += 1
                if apply:
                    client.pages.update(page_id=pid, properties={args.task_status: {"status": {"name": args.task_done}}})
                ensure_completion_note(client, pid, apply)

            # Only create subtasks once per page (no duplicate check beyond existence of list)
            if subtasks:
                ensure_subtasks(client, pid, subtasks, apply)

        if not q.get("has_more"):
            break
        cursor = q.get("next_cursor")

    print(f"Summary: scanned {total} pages; status updates: {updated}{' (applied)' if apply else ' (dry-run)'}")


if __name__ == "__main__":
    main()

