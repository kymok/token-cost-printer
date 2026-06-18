# Codex Token Receipt Printer 仕様書 v0.1

## ドキュメント構成

- [イベント入力](./events.md)
- [データモデル](./data-model.md)
- [レシート仕様](./receipts.md)
- [設定とプリンタ出力](./configuration.md)
- [運用と実装順](./operations.md)

## 1. 目的

PR 情報を受け取る状態なし CLI として、その branch に関連する Codex thread の token usage をサーマルプリンタへ印字する。

---

## 2. 方針

### 基本方針

- 印字対象は `Input` と `Output` のみ。
- token usage は `~/.codex/state_5.sqlite` の `threads` と `rollout_path` の JSONL から読む。
- `cached_input_tokens` は input の内数として扱い、印字しない。
- 自前 DB は持たない。同じ PR を再印字するかどうかは呼び出し側が決める。
- API usage 監査ではなく **Codex ローカル状態から読める observed total** として扱う。

---

## 3. 対象範囲

### 対象

| 機能 | 内容 |
|---|---|
| thread usage 読み取り | Codex SQLite の `threads` から branch 関連 thread を取得 |
| token breakdown 読み取り | 各 thread の `rollout_path` JSONL から最新 `token_count` を取得 |
| PR receipt | PR branch の thread usage 合計を印字 |
| サーマル印字 | ESC/POS 互換プリンタへ印字 |

## 4. 全体構成

```text
Codex app
  └─ ~/.codex/state_5.sqlite
       └─ threads.rollout_path
            └─ rollout JSONL token_count
                 └─ CLI が ESC/POS 印字
```
