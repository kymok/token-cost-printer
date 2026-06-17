# 運用と実装順

## 1. 複数 thread

- `thread_id` ごとに snapshot / checkpoint を持つ。
- turn history は thread ごとの差分として記録する。

## 2. 同一 branch の複数 thread

- PR receipt は PR branch に帰属できた turn history を印字する。

---

## 3. エラー処理

| エラー | 処理 |
|---|---|
| usage snapshot がない | 印字しない |
| Git repo でない | repo 名を `unknown` として扱う |
| USB printer が見つからない | 印字しない |
| プリンタ失敗 | stderr に記録し、DB checkpoint は更新しない |
| delta が負値 | usage reset とみなし current を delta として扱う |
| 同じ PR の再検出 | `printed_prs` によりスキップ |

---

## 4. 実装優先順位

### MVP

1. `agent-turn-complete` notify を受ける
2. SQLite に checkpoint を保存する
3. branch turn history を更新する
4. PR 作成完了 hook を受ける
5. ESC/POS で PR receipt を印字する
