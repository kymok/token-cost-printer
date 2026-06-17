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
cut = true
```

### 1.2 印字幅

```toml
[receipt]
columns = 42
font = "9x17"
```

---

## 2. 設定ファイル

`~/.config/codex-receipt/config.toml`

```toml
[database]
path = "~/.local/share/codex-receipt/state.sqlite3"

[printer]
driver = "escpos"
transport = "usb"
manufacturer = "EPSON"
vendor_id = "0x04b8"
product_id = "0x0e1f"
device = ""
encoding = "cp932"
cut = true

[receipt]
columns = 42
font = "9x17"
print_turn_receipt = true
print_pr_receipt = true
```

`device` が空なら macOS の USB VID/PID lookup で USB device URI を自動設定する。
