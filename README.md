# token-cost-printer

Codex のローカル状態から、PR ブランチに紐づく thread の token usage を集計し、レシート形式で表示または ESC/POS 互換プリンタへ印字する CLI です。

## インストール

Python 3.11 以上が必要です。

```sh
python3 -m pip install -e .
```

インストール後、`codex-receipt` コマンドが使えます。

## まず表示だけ試す

```sh
codex-receipt print \
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

プリンタデバイスを直接指定できます。

```sh
codex-receipt print \
  --repo-root /path/to/repo \
  --pr-number 123 \
  --pr-title "Add receipt printer" \
  --target-branch main \
  --pr-branch feature/receipt \
  --additions 42 \
  --deletions 7 \
  --summary "Prints Codex token usage for this PR." \
  --device /dev/usb/lp0
```

または `~/.config/codex-receipt/config.toml` に設定します。

```toml
[printer]
device = "/dev/usb/lp0"
encoding = "cp932"
cut = true
kanji = true

[receipt]
columns = 35
```

## 何を集計するか

`codex-receipt` はデフォルトで `~/.codex/state_5.sqlite` を読み、指定した `--pr-branch` と一致する Codex thread を探します。各 thread の rollout JSONL から最新の `token_count` を読み、Input、Output、Reasoning、Total を合計します。

別の state DB を使う場合は `--state-db` を指定します。

```sh
codex-receipt print ... --state-db /path/to/state.sqlite --dry-run
```

## 詳細

内部仕様は [docs/README.md](docs/README.md) を参照してください。
