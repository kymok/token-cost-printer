from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Usage:
    input: int = 0
    cached: int = 0
    output: int = 0
    reasoning: int = 0
    total: int = 0
