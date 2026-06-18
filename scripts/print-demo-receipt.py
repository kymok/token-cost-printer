#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import codex_receipt


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="codex-receipt-demo-") as d:
        root = Path(d)
        rollout = root / "rollout.jsonl"
        rollout.write_text(
            json.dumps(
                {
                    "type": "event_msg",
                    "payload": {
                        "type": "token_count",
                        "info": {
                            "total_token_usage": {
                                "input_tokens": 1_200_000,
                                "cached_input_tokens": 1_056_000,
                                "output_tokens": 10_000,
                                "reasoning_output_tokens": 2_000,
                                "total_tokens": 1_210_000,
                            }
                        },
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        db = root / "state.sqlite"
        con = sqlite3.connect(db)
        con.execute("CREATE TABLE threads (id TEXT, git_origin_url TEXT, git_branch TEXT, cwd TEXT, tokens_used INTEGER, rollout_path TEXT, title TEXT, updated_at_ms INTEGER)")
        con.execute("INSERT INTO threads VALUES ('demo', '', 'demo/cost-estimate', ?, 0, ?, 'Demo cost receipt', 0)", (str(root), str(rollout)))
        con.commit()
        con.close()
        return codex_receipt.main(
            [
                "print",
                "--repo-root",
                str(root),
                "--pr-number",
                "999",
                "--pr-title",
                "Demo cost receipt",
                "--target-branch",
                "main",
                "--pr-branch",
                "demo/cost-estimate",
                "--additions",
                "42",
                "--deletions",
                "7",
                "--summary",
                "Fixed dummy data for printer validation.",
                "--state-db",
                str(db),
                *sys.argv[1:],
            ]
        )


if __name__ == "__main__":
    raise SystemExit(main())
