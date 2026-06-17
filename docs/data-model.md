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

## 3. `branch_turn_history`

| column | note |
|---|---|
| `id` | primary key |
| `repo_root` | required |
| `branch_name` | required |
| `turn_id` | required |
| `input_delta` | required |
| `output_delta` | required |
| `updated_at` | required |

## 4. `pr_checkpoints`

| column | note |
|---|---|
| `repo_root` | primary key with `branch_name` |
| `branch_name` | primary key with `repo_root` |
| `last_pr_number` | nullable |
| `history_id` | nullable |
| `updated_at` | required |

## 5. `printed_prs`

| column | note |
|---|---|
| `repo_root` | primary key with `pr_number` |
| `pr_number` | primary key with `repo_root` |
| `printed_at` | required |
