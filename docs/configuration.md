# 設定とプリンタ出力

## 1. プリンタ出力

### 1.1 設定

```toml
[printer]
driver = "escpos"
transport = "usb"
device = "/dev/tty.usbserial"
encoding = "cp932"
cut = true
```

### 1.2 印字幅

```toml
[receipt]
columns = 46
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
device = "/dev/tty.usbserial"
encoding = "cp932"
cut = true

[receipt]
columns = 46
font = "9x17"
print_turn_receipt = true
print_pr_receipt = true
```
