# レシート仕様

## 1. thread usage 仕様

### 1.1 トリガー

`codex-receipt print` を実行したとき。

### 1.2 処理

1. CLI 引数から `--repo-root`, `--pr-branch` を取得する。
2. `--repo-root` から `git_origin_url` を取得する。
3. `~/.codex/state_5.sqlite` の `threads` を `git_origin_url` と `--pr-branch` で絞る。
4. 各 thread の `rollout_path` JSONL から最新 `token_count` を読む。
5. thread ごとの input / output を合算する。
6. JSONL が読めない thread は `threads.tokens_used` を total fallback として扱う。

### 1.3 集計

| 表示 | 元データ |
|---|---|
| Input | `total_token_usage.input_tokens` |
| Output | `total_token_usage.output_tokens` |
| Total | `total_token_usage.total_tokens` |

`cached_input_tokens` は input の内数、`reasoning_output_tokens` は output の内数なので印字しない。

### 1.4 対象 thread

`threads.git_origin_url` と `threads.git_branch` が PR の repo / branch に一致する thread。

---

## 2. PR receipt 仕様

### 2.1 トリガー

`codex-receipt print` を実行したとき。

### 2.2 印字フォーマット

```text
-- PR CREATED --

PR #[number]
[PR title]
[target branch] ← [PR branch]
(+[additions] -[deletions])

[summary]

Total Input Tokens[spaces][input]
Total Output Tokens[spaces][output]


-- HISTORY --

MM/DD HH:MM [thread title]
↑[input]/[cached percent] ↓[output] *[reasoning] Total: [total]


"[quote]"
-- [quote source]
```

`-- PR CREATED --` は ESC/POS の中央揃えと太字で印字する。
`-- HISTORY --` は ESC/POS の中央揃えと太字で印字する。
PR title は1行で、35桁を超えたら切り捨てる。
日本語を含む文字列は ESC/POS の漢字モードを有効化し、Shift-JIS 指定で CP932 出力する。
summary は `--summary` で受け取る。5行以内。
Total は35桁。数値は右端に揃える。
quote は同梱 quote から1つ選ぶ。
HISTORY は PR branch に帰属する thread usage を古い順に印字する。
HISTORY は thread ごとに2行印字する。
1行目は `MM/DD HH:MM [thread title]`。
2行目は `↑150K/88% ↓5.3K *1.3K Total: 160K`。
`/[cached percent]` は input に占める `cached_input_tokens` の割合。
`*[reasoning]` は `reasoning_output_tokens`。

quote 例：

```text
"Input is memory. Output is debt."
-- Codex Marginalia

"A pull request is a polite disturbance."
-- CI Proverbs

"Nothing enters main without first becoming paperwork."
-- Anonymous Maintainer
```

## 3. 数値フォーマット

### 3.1 基本

| token 数 | 表示 |
|---:|---:|
| `10` | `10` |
| `999` | `999` |
| `1,000` | `1.0K` |
| `5,300` | `5.3K` |
| `11,000` | `11K` |
| `150,000` | `150K` |
| `1,200,000` | `1.2M` |

表示は小数点と接尾辞込みで 4 桁以内にする。
