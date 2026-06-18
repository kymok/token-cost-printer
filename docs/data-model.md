# データモデル

Codex の利用量は `~/.codex/state_5.sqlite` から読み、自前 DB は持たない。

## 1. Codex `threads`

読み取り専用。

| column | note |
|---|---|
| `id` | thread id |
| `git_origin_url` | repo 判定 |
| `git_branch` | branch 判定 |
| `cwd` | fallback repo 判定 |
| `tokens_used` | total token fallback |
| `rollout_path` | token breakdown JSONL |
| `title` | receipt 表示用 |
| `updated_at_ms` | 並び順 |

## 2. 同梱 quote

本体に架空 quote を 200 個程度同梱する。実行時に1つ選んで印字する。
