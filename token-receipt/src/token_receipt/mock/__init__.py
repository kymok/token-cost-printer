from __future__ import annotations

import argparse


QUOTE = ("Mock receipts should be boring on purpose.", "Printer Bench")


def args() -> argparse.Namespace:
    return argparse.Namespace(
        pr_number="999",
        pr_title="Mock receipt layout check",
        target_branch="main",
        pr_branch="mock/receipt-fixture",
        additions="128",
        deletions="37",
        summary="Fictional PR data for validating printer alignment, wrapping, and token cost rows without reading Codex state.",
    )


def rows() -> list[dict]:
    return [
        {
            "id": "mock-thread-1",
            "title": "Mock implementation thread",
            "model": "gpt-5.5",
            "usage": {"input": 1_200_000, "cached": 1_056_000, "output": 10_000, "reasoning": 2_000, "total": 1_210_000},
        },
        {
            "id": "mock-thread-2",
            "title": "Mock review and polish thread",
            "model": "gpt-5.4-mini",
            "usage": {"input": 42_000, "cached": 18_000, "output": 5_300, "reasoning": 1_100, "total": 47_300},
        },
    ]
