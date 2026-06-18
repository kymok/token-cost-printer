# イベント入力

## 1. CLI 入力

#### 入力元

`codex-receipt print` のコマンドライン引数。

#### 入力

| option | 必須 |
|---|---|
| `--repo-root` | yes |
| `--pr-number` | yes |
| `--pr-title` | yes |
| `--target-branch` | yes |
| `--pr-branch` | yes |
| `--additions` | yes |
| `--deletions` | yes |
| `--summary` | yes |
| `--pr-url` | no |

---

## 2. Codex thread DB

#### 入力元

```text
~/.codex/state_5.sqlite
```

#### 読み取り対象

| table | field |
|---|---|
| `threads` | `id` |
| `threads` | `git_origin_url` |
| `threads` | `git_branch` |
| `threads` | `cwd` |
| `threads` | `tokens_used` |
| `threads` | `rollout_path` |
| `threads` | `title` |
| `threads` | `updated_at_ms` |

PR branch に関連する thread は、`--repo-root` から解決した `git_origin_url` と `--pr-branch` で絞る。

---

## 3. rollout JSONL

#### 入力元

`threads.rollout_path` が指す JSONL。

#### 読み取り対象

最新の `type = event_msg` かつ `payload.type = token_count` を読む。

| field |
|---|
| `payload.info.total_token_usage.input_tokens` |
| `payload.info.total_token_usage.cached_input_tokens` |
| `payload.info.total_token_usage.output_tokens` |
| `payload.info.total_token_usage.reasoning_output_tokens` |
| `payload.info.total_token_usage.total_tokens` |

`cached_input_tokens` は input の内数、`reasoning_output_tokens` は output の内数として扱う。
