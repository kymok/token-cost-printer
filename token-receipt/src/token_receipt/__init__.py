from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path

from . import codex
from . import mock as mock_data
from .formatter import dollars, text_lines, token, usage_lines
from .models import Usage


FALLBACK_QUOTES = [("Input is memory. Output is debt.", "Codex Marginalia")]
DEFAULT_COST_MODEL = "gpt-5.5"
DEFAULT_COSTS = {
    "gpt-5.5": {"input": 5.00, "cached_input": 0.50, "output": 30.00},
    "gpt-5.4": {"input": 2.50, "cached_input": 0.25, "output": 15.00},
    "gpt-5.4-mini": {"input": 0.75, "cached_input": 0.075, "output": 4.50},
}
DISPLAY_MODELS = {
    "gpt-5.5": "GPT-5.5",
    "gpt-5.4": "GPT-5.4",
    "gpt-5.4-mini": "GPT-5.4-Mini",
}
PROG = "token-receipt"


def cost_key(s: str) -> str:
    return s.strip().casefold().replace(" ", "-")


def display_model(s: str) -> str:
    return DISPLAY_MODELS.get(cost_key(s), s)


def costs(cfg: dict) -> dict[str, dict[str, float]]:
    rows = DEFAULT_COSTS | {}
    for row in cfg.get("cost", {}).get("models", []):
        try:
            rows[cost_key(str(row["name"]))] = {
                "input": float(row["input"]),
                "cached_input": float(row["cached_input"]),
                "output": float(row["output"]),
            }
        except (KeyError, TypeError, ValueError):
            pass
    return rows


def quotes() -> list[tuple[str, str]]:
    for path in (Path(__file__).with_name("quotes.jsonl"), Path("quotes.jsonl")):
        try:
            rows = []
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        row = json.loads(line)
                        rows.append((str(row["quote"]), str(row["source"])))
            if rows:
                return rows
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            pass
    return FALLBACK_QUOTES


def row_usage(row: dict) -> Usage:
    if "usage" in row:
        return Usage(**row["usage"])
    return codex.latest_usage(row["rollout_path"], row["tokens_used"])


def render(
    args: argparse.Namespace,
    rows: list[dict],
    columns: int,
    rates: dict[str, float] | None = None,
    quote: tuple[str, str] | None = None,
) -> str:
    usages = [(row, row_usage(row)) for row in rows]
    total = Usage(
        sum(u.input for _, u in usages),
        sum(u.cached for _, u in usages),
        sum(u.output for _, u in usages),
        sum(u.reasoning for _, u in usages),
        sum(u.total for _, u in usages),
    )
    q, source = quote or random.choice(quotes())
    now = datetime.now().isoformat(timespec="seconds")
    lines = [
        "-- PR CREATED --",
        "",
        f"PR #{args.pr_number}",
        *text_lines(args.pr_title, columns),
        *text_lines(f"{args.target_branch} ← {args.pr_branch}", columns),
        f"(+{args.additions} -{args.deletions})",
        "",
        *text_lines(args.summary, columns)[:8],
        "",
        *usage_lines(total, columns, rates),
        "",
        "",
        "-- HISTORY --",
    ]
    for row, usage in usages:
        lines.append("")
        lines += [
            *text_lines(row["title"] or row["id"], columns),
            *([] if not row.get("model") else text_lines(display_model(str(row["model"])), columns)),
            *usage_lines(usage, columns, rates),
        ]
    lines += ["", "", *text_lines(q, columns), f"-- {source}", "", now]
    return "\n".join(lines) + "\n"


def escpos(text: str, encoding: str, cut: bool, kanji: bool = True) -> bytes:
    # ponytail: enough ESC/POS for text receipts; add printer-specific modes when hardware proves it needs them.
    data = bytearray(b"\x1b@")
    if kanji:
        data.extend(b"\x1cC\x01\x1c&")
    for line in text.splitlines(keepends=True):
        if line.strip() in ("-- PR CREATED --", "-- HISTORY --"):
            data.extend(b"\x1ba\x01\x1bE\x01")
            data.extend(line.encode(encoding, errors="replace"))
            data.extend(b"\x1bE\x00\x1ba\x00")
        elif line.startswith("Total:"):
            data.extend(b"\x1ba\x00")
            data.extend(b"\x1bE\x01")
            data.extend(line.encode(encoding, errors="replace"))
            data.extend(b"\x1bE\x00")
        else:
            data.extend(b"\x1ba\x00")
            data.extend(line.encode(encoding, errors="replace"))
    data.extend(b"\n\n")
    if cut:
        data.extend(b"\x1bd\x04")
        data.extend(b"\x1dV\x00")
    return bytes(data)


def send_printer(device: str, data: bytes) -> None:
    if device.startswith("/"):
        with open(device, "ab", buffering=0) as f:
            f.write(data)
        return
    lpr = "/usr/bin/lpr" if Path("/usr/bin/lpr").exists() else "lpr"
    subprocess.run([lpr, "-P", device, "-o", "raw"], input=data, check=True)


def printer_key(s: str) -> str:
    return "".join(c for c in s.casefold() if c.isalnum())


def cups_printers() -> dict[str, str]:
    try:
        enabled = subprocess.check_output(["lpstat", "-e"], text=True, stderr=subprocess.DEVNULL).split()
    except (OSError, subprocess.SubprocessError):
        enabled = []
    printers = {name: name for name in enabled}
    try:
        for line in subprocess.check_output(["lpstat", "-v"], text=True, stderr=subprocess.DEVNULL).splitlines():
            prefix = "device for "
            if line.startswith(prefix) and ": " in line:
                name, value = line[len(prefix) :].split(": ", 1)
                if not enabled or name in printers:
                    printers.setdefault(name, name)
                    printers[name] += "\n" + value
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        current = ""
        for line in subprocess.check_output(["lpstat", "-l", "-p"], text=True, stderr=subprocess.DEVNULL).splitlines():
            if line.startswith("printer "):
                current = line.split()[1]
            if current and (not enabled or current in printers):
                printers.setdefault(current, current)
                printers[current] += "\n" + line
    except (OSError, subprocess.SubprocessError):
        pass
    return printers


def find_printer(model: str) -> str:
    needle = model.casefold()
    key = printer_key(model)
    matches = [
        name
        for name, info in cups_printers().items()
        if needle in info.casefold() or (key and key in printer_key(info))
    ]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise RuntimeError(f"no CUPS printer matches printer.model={model!r}")
    raise RuntimeError(f"multiple CUPS printers match printer.model={model!r}: {', '.join(matches)}")


def config(path: Path) -> dict:
    if path.expanduser().exists():
        with open(path.expanduser(), "rb") as f:
            return tomllib.load(f)
    return {}


def receipt_settings(args: argparse.Namespace) -> tuple[dict, int, dict[str, float]] | int:
    cfg = config(Path(args.config))
    receipt = cfg.get("receipt", {})
    columns = int(args.columns or receipt.get("columns") or 35)
    cost_model = cost_key(args.cost_model or cfg.get("cost", {}).get("model") or DEFAULT_COST_MODEL)
    rates = costs(cfg).get(cost_model)
    if not rates:
        print(f"{PROG}: unknown cost model {cost_model!r}", file=sys.stderr)
        return 2
    return cfg, columns, rates


def output_cmd(args: argparse.Namespace, cfg: dict, text: str) -> int:
    printer = cfg.get("printer", {})
    try:
        if args.dry_run:
            print(text, end="")
            return 0
        device = args.device or printer.get("device") or ""
        if not device and (args.model or printer.get("model")):
            try:
                device = find_printer(args.model or printer["model"])
            except RuntimeError as e:
                print(f"{PROG}: {e}", file=sys.stderr)
                return 2
        if not device:
            print(f"{PROG}: printer device not configured; use --dry-run or set printer.device/model", file=sys.stderr)
            return 2
        send_printer(
            device,
            escpos(
                text,
                printer.get("encoding", "cp932"),
                bool(printer.get("cut", True)),
                bool(printer.get("kanji", True)),
            ),
        )
        return 0
    except (OSError, subprocess.SubprocessError) as e:
        print(f"{PROG}: printer failed: {e}", file=sys.stderr)
        return 2


def print_cmd(args: argparse.Namespace) -> int:
    settings = receipt_settings(args)
    if isinstance(settings, int):
        return settings
    cfg, columns, rates = settings
    try:
        text = render(args, codex.threads(Path(args.state_db).expanduser(), args.repo_root, args.pr_branch), columns, rates)
    except OSError as e:
        print(f"{PROG}: {e}", file=sys.stderr)
        return 2
    return output_cmd(args, cfg, text)


def mock_cmd(args: argparse.Namespace) -> int:
    settings = receipt_settings(args)
    if isinstance(settings, int):
        return settings
    cfg, columns, rates = settings
    text = render(mock_data.args(), mock_data.rows(), columns, rates, mock_data.QUOTE)
    return output_cmd(args, cfg, text)


def add_output_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--config", default="~/.config/token-receipt/config.toml")
    p.add_argument("--columns", type=int)
    p.add_argument("--cost-model")
    p.add_argument("--device")
    p.add_argument("--model")
    p.add_argument("--dry-run", action="store_true")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=PROG)
    sub = p.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("print")
    pr.add_argument("--repo-root", required=True)
    pr.add_argument("--pr-number", required=True)
    pr.add_argument("--pr-title", required=True)
    pr.add_argument("--target-branch", required=True)
    pr.add_argument("--pr-branch", required=True)
    pr.add_argument("--additions", required=True)
    pr.add_argument("--deletions", required=True)
    pr.add_argument("--summary", required=True)
    pr.add_argument("--pr-url")
    pr.add_argument("--state-db", default="~/.codex/state_5.sqlite")
    add_output_args(pr)
    pr.set_defaults(func=print_cmd)
    mock = sub.add_parser("mock")
    add_output_args(mock)
    mock.set_defaults(func=mock_cmd)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
