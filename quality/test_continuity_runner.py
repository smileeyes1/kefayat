#!/usr/bin/env python3
"""Structural regression for autonomous continuity and direct completion behavior."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "autonomy" / "continuity_runner.py"
CONTRACT = ROOT / "governance" / "CONTINUITY_AND_COMPLETION_CONTRACT.md"


def main() -> None:
    assert RUNNER.is_file() and RUNNER.stat().st_size > 0
    text = RUNNER.read_text(encoding="utf-8")
    for marker in (
        "fail-closed",
        "allow-listed",
        "SAFE_STOP",
        "NO-GO",
        "first unmet",
        "completed",
        "evidence-ledger.jsonl",
    ):
        assert marker in text, f"continuity invariant missing: {marker}"
    contract = CONTRACT.read_text(encoding="utf-8")
    for marker in (
        "continue through every executable and verifiable step",
        "real external blocker",
        "system of record",
        "Do not stop merely",
    ):
        assert marker in contract, f"continuity contract missing: {marker}"
    print("CONTINUITY RUNNER REGRESSION: PASS")


if __name__ == "__main__":
    main()
