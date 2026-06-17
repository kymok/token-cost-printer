# レシート仕様

## 1. turn receipt 仕様

### 1.1 トリガー

`agent-turn-complete` を受信したとき。

### 1.2 処理

1. payload から `thread-id`, `turn-id`, `cwd` を取得する。
2. `cwd` から Git repo root を解決する。
3. `cwd` から Git branch name を解決する。
4. `thread_usage_snapshots` から現在 snapshot を読む。
5. `turn_print_checkpoints` から前回印字 snapshot を読む。
6. 差分を計算する。
7. 差分があれば印字する。
8. `turn_print_checkpoints` を更新する。
9. `repo_totals` に差分を加算する。

### 1.3 差分計算

| delta | 計算 |
|---|---|
| input | current input tokens - checkpoint input tokens |
| output | current output tokens - checkpoint output tokens |

負値は usage reset として current を delta にする。

### 1.4 印字フォーマット

```text
[HH:MM] [branch][spaces]I:[input] O:[output]
```

| 項目 | 配置 |
|---|---|
| time | 左端 |
| branch | 左寄せ、溢れたら切り捨て |
| input / output | 4桁幅で右寄せ |
| columns | 42 |
| branch columns | 22 |

```text
12:34 feat/my-very-long-bran I:150K O:5.3K
12:34 feat/branch            I:150K O:5.3K
```

### 1.5 印字条件

input delta または output delta が 0 より大きい。

---

## 2. PR receipt 仕様

### 2.1 トリガー

PR 作成完了 hook を受信したとき。

### 2.2 重複防止

`printed_prs` に `(repo_root, pr_number)` が存在する場合は印字しない。

### 2.3 差分計算

| delta | 計算 |
|---|---|
| input | repo total input tokens - PR checkpoint input tokens |
| output | repo total output tokens - PR checkpoint output tokens |

### 2.4 印字フォーマット

```text

-- PR CREATED --

[target branch] <- [PR branch]
(+[additions] -[deletions])
Total Input:  [input]
Total Output: [output]

"[quote]"
— [fictional source]
```

`-- PR CREATED --` は ESC/POS の中央揃えと太字で印字する。
quote は LLM が生成する架空引用。

例：

```text
"Input is memory. Output is debt."
— Codex Marginalia

"A pull request is a polite disturbance."
— CI Proverbs

"Nothing enters main without first becoming paperwork."
— Anonymous Maintainer
```

### 2.5 印字後更新

`pr_checkpoints` と `printed_prs` を更新する。

---

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
