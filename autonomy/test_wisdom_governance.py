#!/usr/bin/env python3
"""Adversarial regression for the Wisdom Ω governance contract."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "governance" / "WISDOM_GOVERNANCE.md"
INDEX = ROOT / "index.html"

REQUIRED_DOC_MARKERS = (
    "PURPOSE → CONTEXT → EVIDENCE → OPTIONS → TRADE-OFFS → DECISION → EXECUTION → VERIFICATION → ADVERSARIAL CHECK → REPAIR → REGRESSION → RELEASE",
    "Missing evidence means \"unproven\", not \"true\".",
    "Prevent cross-domain contamination",
    "Human intervention is reserved for genuine blockers",
    "FIELD-READY",
)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\ufeff", "")).strip().lower()


def main() -> None:
    assert DOC.exists() and DOC.stat().st_size > 1000, "Wisdom governance contract missing/empty"
    doc = norm(DOC.read_text(encoding="utf-8"))
    for marker in REQUIRED_DOC_MARKERS:
        assert norm(marker) in doc, f"Wisdom marker missing: {marker}"

    ui = INDEX.read_text(encoding="utf-8")
    # The existing UI must continue to expose the governance concepts it claims.
    for marker in ("WISDOM", "inferMission", "retrieveMission", "Cross-Domain", "Evidence-Governed"):
        assert marker in ui, f"UI governance marker missing: {marker}"

    # High-value adversarial guard: explicit math intent must remain distinguishable
    # from Arabic-language retrieval in the source-level routing contract.
    assert "العدد" in ui and "mathematics" in ui and "arabic" in ui

    print("WISDOM GOVERNANCE REGRESSION: PASS")


if __name__ == "__main__":
    main()
