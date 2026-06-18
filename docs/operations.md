# 運用と実装順

## 1. 複数 thread

- Codex SQLite の `threads` を PR branch で絞る。
- 各 thread の `rollout_path` から最新 token usage を読む。

## 2. 同一 branch の複数 thread

- PR receipt は PR branch に帰属できた thread usage 合計を印字する。
- state は持たない。同じ PR を再印字するかどうかは呼び出し側が決める。

---

## 3. エラー処理

| エラー | 処理 |
|---|---|
| Codex SQLite が読めない | 印字しない |
| rollout JSONL が読めない | `threads.tokens_used` を total fallback として扱う |
| Git repo でない | repo 名を `unknown` として扱う |
| USB printer が見つからない | 印字しない |
| プリンタ失敗 | stderr に記録する |

---

## 4. 実装優先順位

### MVP

1. `codex-receipt print` の CLI 引数から PR / branch / summary を受ける
2. Codex SQLite から branch 関連 thread を取得する
3. rollout JSONL から input / output を取得する
4. ESC/POS で PR receipt を印字する
