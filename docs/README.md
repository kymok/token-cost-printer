# Codex Token Receipt Printer 仕様書 v0.1

## ドキュメント構成

- [イベント入力](./events.md)
- [データモデル](./data-model.md)
- [レシート仕様](./receipts.md)
- [設定とプリンタ出力](./configuration.md)
- [運用と実装順](./operations.md)

## 1. 目的

Codex app の利用中に、**PR 作成ごと**に、その branch で観測された token usage 履歴をサーマルプリンタへ印字する。

---

## 2. 方針

### 基本方針

- `Cached` は扱わない。
- 印字対象は `Input` と `Output` のみ。
- token usage は **観測された累積値の delta** として計算する。
- 複数 thread / 複数 repo の並列実行は許容する。
- API usage 監査ではなく **observed delta** として扱う。

---

## 3. 対象範囲

### 対象

| 機能 | 内容 |
|---|---|
| turn history | turn 終了ごとに Input / Output token の delta を記録 |
| PR receipt | PR 作成完了 hook 受信時に、PR branch の履歴を印字 |
| branch 別集計 | `cwd` から Git branch を解決できた turn delta を蓄積 |
| thread 別集計 | `thread-id` ごとに usage snapshot を保持 |
| 状態管理 | MCP server が snapshot / checkpoint / branch history を保持 |
| サーマル印字 | ESC/POS 互換プリンタへ印字 |

## 4. 全体構成

```text
Codex app
  ├─ thread/tokenUsage/updated
  └─ notify: agent-turn-complete
       └─ MCP server
            ├─ turn history 更新
            ├─ SQLite checkpoint 更新
            └─ PR 作成時に ESC/POS 印字
```
