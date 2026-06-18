---
name: codex-receipt-pr
description: Run codex-receipt after creating or publishing a GitHub pull request. Use when Codex creates a PR for this repository and should print, or dry-run, a token usage receipt for that PR.
---

# Codex Receipt PR

After a PR exists, run `codex-receipt print` before the final response.

## Summary

Generate `PR_SUMMARY` from the PR title, body, and diff stat:

```sh
gh pr view --json title,body
gh pr diff --stat
```

Write one sentence, 140 characters or fewer. Summarize what changed; do not copy the PR body heading.
Set it as `PR_SUMMARY` before running the receipt command.

## Receipt

From the repository root, collect PR metadata with `gh` and pass it to `codex-receipt`:

```sh
command -v codex-receipt >/dev/null || python3 -m pip install -e .

PR_JSON="$(gh pr view --json number,title,baseRefName,headRefName,additions,deletions,url)" PR_SUMMARY="$PR_SUMMARY" python3 - <<'PY'
import json
import os
import subprocess
import sys

pr = json.loads(os.environ["PR_JSON"])
repo_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
summary = os.environ["PR_SUMMARY"].strip()[:140]
if not summary:
    raise SystemExit("PR_SUMMARY is required")

cmd = [
    "codex-receipt",
    "print",
    "--repo-root",
    repo_root,
    "--pr-number",
    str(pr["number"]),
    "--pr-title",
    pr["title"],
    "--target-branch",
    pr["baseRefName"],
    "--pr-branch",
    pr["headRefName"],
    "--additions",
    str(pr["additions"]),
    "--deletions",
    str(pr["deletions"]),
    "--summary",
    summary,
    "--pr-url",
    pr["url"],
]

result = subprocess.run(cmd)
if result.returncode == 0:
    raise SystemExit(0)

print("codex-receipt failed; retrying with --dry-run", file=sys.stderr)
raise SystemExit(subprocess.run([*cmd, "--dry-run"]).returncode)
PY
```

Report whether the receipt printed or only dry-ran.
