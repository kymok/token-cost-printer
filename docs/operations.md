# 運用と実装順

## 1. 複数 thread

- `thread_id` ごとに snapshot / checkpoint を持つ。
- turn receipt は thread ごとの差分として計算する。

## 2. 同一 repo の複数 thread

- repo total は MCP server が repo に帰属できた turn delta の合算。
- PR receipt は前回 PR 以降の repo total delta を印字する。

---

## 3. エラー処理

| エラー | 処理 |
|---|---|
| usage snapshot がない | 印字しない |
| Git repo でない | repo 名を `unknown` として扱う |
| プリンタ失敗 | stderr に記録し、DB checkpoint は更新しない |
| delta が負値 | usage reset とみなし current を delta として扱う |
| 同じ PR の再検出 | `printed_prs` によりスキップ |

---

## 4. 実装優先順位

### MVP

1. `agent-turn-complete` notify を受ける
2. SQLite に checkpoint を保存する
3. ESC/POS で turn receipt を印字する
4. repo total を更新する
5. PR 作成完了 hook を受ける
6. ESC/POS で PR receipt を印字する
