from __future__ import annotations

import unicodedata
from collections.abc import Mapping
from typing import Any


MIN_COLUMNS = 35


def require_columns(columns: int) -> None:
    if columns < MIN_COLUMNS:
        raise ValueError(f"columns must be at least {MIN_COLUMNS}")


def width(s: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in "FW" else 1 for c in s)


def clip(s: str, columns: int) -> str:
    out = ""
    used = 0
    for c in s:
        w = 2 if unicodedata.east_asian_width(c) in "FW" else 1
        if used + w > columns:
            break
        out += c
        used += w
    return out


def right(label: str, value: str, columns: int) -> str:
    require_columns(columns)
    return label + " " * max(1, columns - width(label) - width(value)) + value


def token(n: int) -> str:
    if n < 1000:
        return str(n)
    for suffix, base in (("M", 1_000_000), ("K", 1000)):
        if n >= base:
            v = n / base
            return (f"{v:.1f}" if v < 10 else f"{v:.0f}") + suffix
    return str(n)


def usd(value: float) -> str:
    return f"{value:.2f} USD"


def dollars(usage: Any, rates: Mapping[str, float]) -> str:
    uncached = max(usage.input - usage.cached, 0)
    value = (uncached * rates["input"] + usage.cached * rates["cached_input"] + usage.output * rates["output"]) / 1_000_000
    return usd(value)


def usage_costs(usage: Any, rates: Mapping[str, float]) -> dict[str, str]:
    input_cost = (max(usage.input - usage.cached, 0) * rates["input"] + usage.cached * rates["cached_input"]) / 1_000_000
    output_cost = usage.output * rates["output"] / 1_000_000
    return {
        "Input:": usd(input_cost),
        "Output:": usd(output_cost),
        "Reasoning:": usd(usage.reasoning * rates["output"] / 1_000_000),
        "Total:": usd(input_cost + output_cost),
    }


def usage_lines(usage: Any, columns: int, rates: Mapping[str, float] | None = None) -> list[str]:
    require_columns(columns)
    cached = round(usage.cached * 100 / usage.input) if usage.input else 0
    cached_text = f" (C:{cached}%)"
    values = {
        "Input:": token(usage.input),
        "Output:": token(usage.output),
        "Reasoning:": token(usage.reasoning),
        "Total:": token(usage.total),
    }
    value_end = max(map(width, values)) + 1 + max(width(v) for v in values.values())

    def line(label: str, value: str, suffix: str = "") -> str:
        text = label + " " * max(1, value_end - width(label) - width(value)) + value + suffix
        if rates:
            cost = usage_costs(usage, rates)[label]
            if width(text) + 1 + width(cost) > columns:
                text = clip(text, columns - width(cost) - 1)
            return text + " " * max(1, columns - width(text) - width(cost)) + cost
        return text

    return [
        line("Input:", values["Input:"], cached_text),
        line("Output:", values["Output:"]),
        line("Reasoning:", values["Reasoning:"]),
        line("Total:", values["Total:"]),
    ]


def wrap_lines(text: str, columns: int) -> list[str]:
    require_columns(columns)
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = f"{line} {word}" if line else word
        if width(candidate) <= columns:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    return lines + ([line] if line else [])


def quote_lines(quote: str, columns: int) -> list[str]:
    return wrap_lines(quote.replace(";", ""), columns)


def summary_lines(summary: str, columns: int) -> list[str]:
    return [line for paragraph in summary.splitlines() for line in wrap_lines(paragraph, columns)][:8]
