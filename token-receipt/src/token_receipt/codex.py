from __future__ import annotations

import json
import sqlite3
import subprocess
from pathlib import Path

from .models import Usage


def latest_usage(path: str | None, fallback_total: int | None) -> Usage:
    if path:
        try:
            latest = None
            with open(Path(path).expanduser(), encoding="utf-8") as f:
                for line in f:
                    row = json.loads(line)
                    payload = row.get("payload", {})
                    if row.get("type") == "event_msg" and payload.get("type") == "token_count":
                        latest = payload.get("info", {}).get("total_token_usage", {})
            if latest:
                return Usage(
                    int(latest.get("input_tokens") or 0),
                    int(latest.get("cached_input_tokens") or 0),
                    int(latest.get("output_tokens") or 0),
                    int(latest.get("reasoning_output_tokens") or 0),
                    int(latest.get("total_tokens") or 0),
                )
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    return Usage(total=int(fallback_total or 0))


def git_origin(repo_root: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", repo_root, "config", "--get", "remote.origin.url"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.SubprocessError:
        return ""


def threads(state_db: Path, repo_root: str, branch: str) -> list[dict]:
    origin = git_origin(repo_root)
    root = str(Path(repo_root).resolve())
    con = sqlite3.connect(state_db.expanduser())
    con.row_factory = sqlite3.Row
    try:
        thread_columns = {row[1] for row in con.execute("PRAGMA table_info(threads)")}
        model_column = ", model" if "model" in thread_columns else ""
        rows = con.execute(
            f"""
            SELECT id, git_origin_url, git_branch, cwd, tokens_used, rollout_path, title, updated_at_ms{model_column}
            FROM threads
            WHERE git_branch = ?
            ORDER BY updated_at_ms
            """,
            (branch,),
        ).fetchall()
    finally:
        con.close()
    return [
        dict(r)
        for r in rows
        if (origin and r["git_origin_url"] == origin)
        or (not origin and r["cwd"] and str(Path(r["cwd"]).resolve()).startswith(root))
    ]
