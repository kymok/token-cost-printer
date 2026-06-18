# 設定とプリンタ出力

## 1. プリンタ出力

### 1.1 設定

```toml
[printer]
driver = "escpos"
transport = "usb"
manufacturer = "EPSON"
vendor_id = "0x04b8"
product_id = "0x0e1f"
model = "EPSON TM-m10"
device = ""
encoding = "cp932"
kanji = "shift_jis"
cut = true
```

### 1.2 印字幅

```toml
[receipt]
font = "A"
scale = 1
columns = 35
font_a_columns = 35
```

---

## 2. 設定ファイル

`~/.config/codex-receipt/config.toml`

```toml
[printer]
driver = "escpos"
transport = "usb"
manufacturer = "EPSON"
vendor_id = "0x04b8"
product_id = "0x0e1f"
model = "EPSON TM-m10"
device = ""
encoding = "cp932"
kanji = "shift_jis"
cut = true

[receipt]
font = "A"
scale = 1
columns = 35
font_a_columns = 35
print_pr_receipt = true

[cost]
model = "gpt-5.5"

[[cost.models]]
name = "custom"
input = 1.0
cached_input = 0.1
output = 2.0
```

`model` は CUPS の有効プリンタ一覧から部分一致で自動選択する機種名。
`device` は `/dev/usb/lp0` のようなデバイスパス、または `EPSON_TM_m10_JPN` のようなCUPSプリンタ名。指定すると `model` より優先される。
TM-m10 の58mm紙は Font A で35cpl。
`cost.model` は `gpt-5.5`、`gpt-5.4`、`gpt-5.4-mini` を同梱。`[[cost.models]]` で同じ名前を書くと上書きできる。
