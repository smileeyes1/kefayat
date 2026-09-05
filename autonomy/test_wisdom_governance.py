#!/usr/bin/env python3
"""Adversarial regression for the Wisdom Ω governance contract."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "governance" / "WISDOM_GOVERNANCE.md"
INTENT = ROOT / "governance" / "INTENT_FULFILLMENT_CONTRACT.md"
ENGINE = ROOT / "intent" / "intent-engine.js"
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

    assert INTENT.exists() and INTENT.stat().st_size > 1000, "Intent fulfillment governance missing/empty"
    intent_doc = INTENT.read_text(encoding="utf-8")
    for marker in ("INTENT CONTRACT", "Acceptance Oracle", "Cross-Domain", "actual PDF", "Zero-burden"):
        assert marker.lower() in intent_doc.lower(), f"Intent governance marker missing: {marker}"

    ui = INDEX.read_text(encoding="utf-8")
    engine = ENGINE.read_text(encoding="utf-8")
    # The shipped UI must expose the governance concepts it claims.
    for marker in ("WISDOM", "inferMission", "retrieveMission", "Cross-Domain", "Evidence-Governed", "Intent Contract", "Acceptance Oracle"):
        assert marker in ui, f"UI governance marker missing: {marker}"

    # High-value adversarial guard: math-number intent is owned by the deterministic
    # intent engine, not by a brittle duplicated keyword in the presentation shell.
    for marker in ("mathematics", "arabic", "عدد", "detectSubject", "compileContract"):
        assert marker in engine, f"Intent engine routing marker missing: {marker}"

    print("WISDOM GOVERNANCE REGRESSION: PASS")


if __name__ == "__main__":
    main()
