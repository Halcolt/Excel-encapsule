"""Notion subproject utility: write-protection gate."""
import os


def require_write_access() -> None:
    """Abort if NOTION_ALLOW_WRITE is not explicitly true.

    This enforces that the project uses Notion for documentation/PM only by default,
    and avoids accidental content changes. To enable writes for a specific, intentional
    task, set NOTION_ALLOW_WRITE=true in the environment.
    """
    allow = os.environ.get("NOTION_ALLOW_WRITE", "false").lower()
    if allow not in {"1", "true", "yes"}:
        raise SystemExit(
            "Notion write operations are disabled. Set NOTION_ALLOW_WRITE=true to enable."
        )
