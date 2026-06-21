# token-receipt

Codex のローカル状態から、PR ブランチに紐づく thread の token usage を集計し、レシート形式で表示または ESC/POS 互換プリンタへ印字する CLI です。

## インストール

Python 3.11 以上と `pipx` が必要です。

```sh
brew install pipx
pipx ensurepath
pipx install --editable ./token-receipt
```

インストール後、`token-receipt` コマンドが使えます。

アンインストール:

```sh
pipx uninstall token-receipt
```

## まず表示だけ試す

```sh
token-receipt print \
  --repo-root /path/to/repo \
  --pr-number 123 \
  --pr-title "Add receipt printer" \
  --target-branch main \
  --pr-branch feature/receipt \
  --additions 42 \
  --deletions 7 \
  --summary "Prints Codex token usage for this PR." \
  --dry-run
```

`--dry-run` はプリンタへ送らず、標準出力にレシート内容を表示します。

## 印字する

プリンタを直接指定できます。

```sh
token-receipt print \
  --repo-root /path/to/repo \
  --pr-number 123 \
  --pr-title "Add receipt printer" \
  --target-branch main \
  --pr-branch feature/receipt \
  --additions 42 \
  --deletions 7 \
  --summary "Prints Codex token usage for this PR." \
  --device EPSON_TM_m10_JPN
```

または `~/.config/token-receipt/config.toml` に設定します。

```sh
token-receipt setup
token-receipt setup EPSON_TM
```

`setup` は空なら CUPS デバイス一覧を表示します。引数ありなら CUPS の有効プリンタ名を先頭一致で探し、1件だけ一致した名前を `printer.device` に保存します。

```toml
[printer]
model = "EPSON TM-m10"
encoding = "cp932"
cut = true
kanji = true

[receipt]
columns = 42

[cost]
model = "gpt-5.5"
```

`device` には CUPS プリンタ名を指定します。
TM-m10 は CUPS 名の一致で Font B、42桁（漢字21桁）になります。

## 実機確認用のダミー印字

```sh
token-receipt mock --dry-run
token-receipt mock
```

追加の `--device`、`--model`、`--config`、`--cost-model` は `mock` でも使えます。

## 何を集計するか

`token-receipt` はデフォルトで `~/.codex/state_5.sqlite` を読み、指定した `--pr-branch` と一致する Codex thread を探します。各 thread の rollout JSONL から最新の `token_count` を読み、Input、Output、Reasoning、Total を合計し、各行の右端に cost を表示します。

別の state DB を使う場合は `--state-db` を指定します。

```sh
token-receipt print ... --state-db /path/to/state.sqlite --dry-run
```

## 詳細

内部仕様は [docs/README.md](docs/README.md) を参照してください。
