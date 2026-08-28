#!/usr/bin/env python3
"""Kefayat Ω static release-contract regression.

This contract is conservative: it proves prerequisites that can be checked without a
browser or a human device. It fails closed when a required artifact, knowledge source,
routing guard, production contract, or Pages deployment contract disappears.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
AI = ROOT / "ai.html"
KB = ROOT / "knowledge" / "competencies.json"
MATH = ROOT / "raw_sources" / "math_grade_1.txt"
NURTURING = ROOT / "raw_sources" / "nurturing_grade_1.txt"
PAGES = ROOT / ".github" / "workflows" / "pages.yml"
PROD = ROOT / "quality" / "test_production_contract.py"
WISDOM = ROOT / "governance" / "WISDOM_GOVERNANCE.md"


def main() -> None:
    for p, minimum in ((INDEX, 1000), (AI, 1000), (KB, 1000), (MATH, 1000), (NURTURING, 500), (PROD, 1000), (WISDOM, 1000)):
        assert p.exists(), f"required artifact missing: {p}"
        assert p.stat().st_size > minimum, f"required artifact too small: {p}"
    assert PAGES.exists(), "GitHub Pages workflow missing"

    kb = json.loads(KB.read_text(encoding="utf-8"))
    records = kb.get("records")
    assert isinstance(records, list) and records, "knowledge records missing"
    assert isinstance(kb.get("coverage"), list) and kb["coverage"], "knowledge coverage missing"

    required_pairs = {
        (1, "arabic"), (1, "mathematics"), (1, "islamic_education"), (1, "nurturing")
    }
    present = {(r.get("grade"), r.get("subject")) for r in records}
    assert required_pairs <= present, f"Grade 1 coverage incomplete: missing={sorted(required_pairs-present)}"

    ids = [r.get("id") for r in records]
    assert all(ids) and len(ids) == len(set(ids)), "competency IDs must be present and unique"
    assert all(isinstance(r.get("provenance"), dict) and r["provenance"].get("status") for r in records), "provenance missing"
    assert all(isinstance(r.get("source_text"), str) and r["source_text"].strip() for r in records), "source text missing"

    math_text = MATH.read_text(encoding="utf-8")
    assert "العدد 1" in math_text or "العدد ١" in math_text, "Grade 1 number-1 competency not present"

    page_text = PAGES.read_text(encoding="utf-8")
    for required in (
        "actions/configure-pages@v5",
        "actions/upload-pages-artifact@v4",
        "actions/deploy-pages@v4",
        "pages: write",
        "id-token: write",
        "python tools/build_competencies.py",
        "python autonomy/test_intent_routing.py",
        "python autonomy/test_wisdom_governance.py",
        "python quality/test_production_contract.py",
    ):
        assert required in page_text, f"Pages release gate missing: {required}"

    ui = INDEX.read_text(encoding="utf-8")
    routing_markers = ("inferMission", "retrieveMission", "mathematics", "subject", "WISDOM", "localStorage")
    assert all(marker in ui for marker in routing_markers), "core UI contract markers missing"

    ai = AI.read_text(encoding="utf-8")
    for marker in ("Gemini", "Free-First", "localStorage", "لا خادم مدفوع"):
        assert marker in ai, f"AI/free-first contract marker missing: {marker}"

    print("RELEASE CONTRACT REGRESSION: PASS")


if __name__ == "__main__":
    main()
