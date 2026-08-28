#!/usr/bin/env python3
"""Continuity/completion gate: authorized work must have an explicit resumable path."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    runner = (ROOT / "autonomy" / "continuity_runner.py").read_text(encoding="utf-8")
    contract = (ROOT / "governance" / "CONTINUITY_AND_COMPLETION_CONTRACT.md").read_text(encoding="utf-8")
    for marker in ("STAGES", "SAFE_STOP", "NO-GO", "first unmet", "evidence-ledger.jsonl"):
        haystack = runner + "\n" + contract
        assert marker.lower() in haystack.lower(), f"continuity marker missing: {marker}"
    assert "Do not stop merely because an intermediate step succeeded" in contract
    assert "human authority decision is genuinely required" in contract
    assert "FIELD-READY" in contract
    print("CONTINUITY & COMPLETION GATE: PASS")


if __name__ == "__main__":
    main()
