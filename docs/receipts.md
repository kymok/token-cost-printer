# レシート仕様

## 1. thread usage 仕様

### 1.1 トリガー

`token-receipt print` を実行したとき。

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

`token-receipt print` を実行したとき。

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

[thread title]
[model]
Input: [input] (C: [cached percent]) [cost]
Output: [output] [cost]


"[quote]"
-- [quote source]
```

`-- PR CREATED --` は ESC/POS の中央揃えと太字で印字する。
`-- HISTORY --` は ESC/POS の中央揃えと太字で印字する。
PR title はプリンタプロファイルの桁数で折り返す。
日本語を含む文字列は ESC/POS の漢字モードを有効化し、Shift-JIS 指定で CP932 出力する。
summary は `--summary` で受け取る。8行以内。
Total はプリンタプロファイルの桁数内で、数値を右端に揃える。
Cost は `xxx.xx USD` 形式で各 usage 行の右端に印字する。
quote は同梱 quote から1つ選ぶ。
HISTORY は PR branch に帰属する thread usage を古い順に印字する。
HISTORY は thread ごとに title の1行目、model、usage だけを印字する。
`(C: [cached percent])` は input に占める `cached_input_tokens` の割合。

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
