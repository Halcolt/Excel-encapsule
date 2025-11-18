"""
Update Task and Milestone databases: enrich details and set status for completed items.

This script is generic: provide database IDs and property names via env or CLI.

Completion rule (tasks):
- If a boolean property (e.g., "Completed") is true, or
- If a numeric/percentage property (e.g., "Checklist Done %") equals 100 (or >= 1.0),
then set the Status property to the DONE value.

Env (or CLI overrides):
- NOTION_TOKEN (required)
- NOTION_ALLOW_WRITE=true (required to apply changes)
- TASK_DB_ID (optional)
- MILESTONE_DB_ID (optional)
- TASK_STATUS_PROPERTY (default: Status)
- TASK_DONE_VALUE (default: Done)
- TASK_COMPLETED_CHECKBOX (optional; e.g., Completed)
- TASK_CHECKLIST_NUMERIC (optional; e.g., Checklist Done %)
- MILESTONE_STATUS_PROPERTY (default: Status)
- MILESTONE_DONE_VALUE (default: Done)

Dry run by default; pass --apply or set APPLY_CHANGES=true to write.

Usage (from projects/notion):
  docker compose run --rm app python notion_update_tasks_milestones.py --apply \
    --tasks $env:TASK_DB_ID --milestones $env:MILESTONE_DB_ID
"""
import os
import argparse
from typing import Any, Dict, Optional
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


def set_status(client: Client, page_id: str, prop: str, value: str, apply: bool) -> None:
    print(f"  -> set {prop} = {value}")
    if apply:
        client.pages.update(page_id=page_id, properties={prop: {"status": {"name": value}}})


def process_db(client: Client, db_id: str, kind: str, status_prop: str, done_value: str,
               completed_checkbox: Optional[str], completed_numeric: Optional[str], apply: bool) -> None:
    print(f"\n== Processing {kind} database: {db_id} ==")
    cursor = None
    count = 0
    updates = 0
    while True:
        kwargs = {"database_id": db_id, "page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor
        q = client.databases.query(**kwargs)
        for page in q.get("results", []):
            count += 1
            current = status_name(page, status_prop)
            pid = page.get("id")
            title = next(("".join(rt.get("plain_text", "") for rt in v.get("title", []))
                          for k, v in page.get("properties", {}).items() if v.get("type") == "title"), pid)
            print(f"- {title} [{current or '-'}]")
            should_done = False
            if completed_checkbox:
                val = checkbox_value(page, completed_checkbox)
                should_done = should_done or bool(val)
            if completed_numeric is not None:
                num = number_value(page, completed_numeric)
                if num is not None:
                    should_done = should_done or (num >= 100 or num >= 1.0)
            if should_done and current != done_value:
                updates += 1
                set_status(client, pid, status_prop, done_value, apply)
        if not q.get("has_more"):
            break
        cursor = q.get("next_cursor")
    print(f"Summary: scanned {count} pages; updates: {updates}{' (applied)' if apply else ' (dry-run)'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", dest="task_db")
    ap.add_argument("--milestones", dest="milestone_db")
    ap.add_argument("--task-status", default=os.environ.get("TASK_STATUS_PROPERTY", "Status"))
    ap.add_argument("--task-done", default=os.environ.get("TASK_DONE_VALUE", "Done"))
    ap.add_argument("--task-completed", dest="task_completed_checkbox",
                    default=os.environ.get("TASK_COMPLETED_CHECKBOX"))
    ap.add_argument("--task-checklist", dest="task_checklist_numeric",
                    default=os.environ.get("TASK_CHECKLIST_NUMERIC"))
    ap.add_argument("--milestone-status", default=os.environ.get("MILESTONE_STATUS_PROPERTY", "Status"))
    ap.add_argument("--milestone-done", default=os.environ.get("MILESTONE_DONE_VALUE", "Done"))
    ap.add_argument("--apply", action="store_true", help="Apply changes instead of dry-run")
    args = ap.parse_args()

    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("NOTION_TOKEN is required")

    # Require write access if applying
    apply = bool(args.apply or os.environ.get("APPLY_CHANGES", "").lower() in {"1", "true", "yes"})
    if apply:
        require_write_access()

    client = Client(auth=token)

    task_db = args.task_db or os.environ.get("TASK_DB_ID")
    mile_db = args.milestone_db or os.environ.get("MILESTONE_DB_ID")

    if not task_db and not mile_db:
        raise SystemExit("Provide --tasks <db_id> and/or --milestones <db_id> (or env TASK_DB_ID/MILESTONE_DB_ID)")

    if task_db:
        process_db(client, task_db, "Tasks", args.task_status, args.task_done,
                   args.task_completed_checkbox, args.task_checklist_numeric, apply)
    if mile_db:
        process_db(client, mile_db, "Milestones", args.milestone_status, args.milestone_done,
                   None, None, apply)


if __name__ == "__main__":
    main()

