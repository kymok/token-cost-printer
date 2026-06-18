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
```

`device` は `/dev/usb/lp0` のようなデバイスパス、または `EPSON_TM_m10_JPN` のようなCUPSプリンタ名。
TM-m10 の58mm紙は Font A で35cpl。
