# データモデル

SQLite を使用する。

## 1. `thread_usage_snapshots`

| column | note |
|---|---|
| `thread_id` | primary key |
| `repo_root` | nullable |
| `input_tokens` | default 0 |
| `output_tokens` | default 0 |
| `updated_at` | required |

## 2. `turn_print_checkpoints`

| column | note |
|---|---|
| `thread_id` | primary key |
| `input_tokens` | default 0 |
| `output_tokens` | default 0 |
| `last_turn_id` | nullable |
| `updated_at` | required |

## 3. `repo_totals`

| column | note |
|---|---|
| `repo_root` | primary key |
| `repo_name` | required |
| `input_tokens` | default 0 |
| `output_tokens` | default 0 |
| `updated_at` | required |

## 4. `pr_checkpoints`

| column | note |
|---|---|
| `repo_root` | primary key |
| `last_pr_number` | nullable |
| `input_tokens` | default 0 |
| `output_tokens` | default 0 |
| `updated_at` | required |

## 5. `printed_prs`

| column | note |
|---|---|
| `repo_root` | primary key with `pr_number` |
| `pr_number` | primary key with `repo_root` |
| `printed_at` | required |
