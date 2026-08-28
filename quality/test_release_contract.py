#!/usr/bin/env python3
"""Kefayat Ω static release-contract regression.

This test is deliberately conservative: it proves release prerequisites that can be
checked without a browser or a human device. It must fail closed when a required
artifact, knowledge source, routing guard, or Pages deployment contract disappears.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
KB = ROOT / "knowledge" / "competencies.json"
MATH = ROOT / "raw_sources" / "math_grade_1.txt"
PAGES = ROOT / ".github" / "workflows" / "pages.yml"


def main() -> None:
    assert INDEX.exists(), "index.html missing"
    assert INDEX.stat().st_size > 1000, "index.html is unexpectedly small"
    assert KB.exists() and KB.stat().st_size > 1000, "structured knowledge artifact missing/empty"
    assert MATH.exists() and MATH.stat().st_size > 1000, "Grade 1 mathematics source missing/empty"
    assert PAGES.exists(), "GitHub Pages workflow missing"

    kb = json.loads(KB.read_text(encoding="utf-8"))
    records = kb.get("records")
    assert records and isinstance(records, list), "knowledge records missing"
    assert kb.get("coverage") and isinstance(kb["coverage"], list), "knowledge coverage missing"

    math_records = [r for r in records if r.get("grade") == 1 and r.get("subject") == "mathematics"]
    arabic_records = [r for r in records if r.get("grade") == 1 and r.get("subject") == "arabic"]
    assert math_records, "Grade 1 mathematics records missing"
    assert arabic_records, "Grade 1 Arabic records missing; negative cross-domain guard cannot be exercised"

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
    ):
        assert required in page_text, f"Pages release gate missing: {required}"

    # The UI must contain the actual routing contract. The test intentionally
    # does not require a particular competency ID to be hard-coded into the UI.
    # Negative cross-domain evidence belongs in the structured knowledge tests.
    ui = INDEX.read_text(encoding="utf-8")
    routing_markers = ("inferMission", "retrieveMission", "mathematics", "subject", "WISDOM")
    assert all(marker in ui for marker in routing_markers), "routing contract markers missing from UI"

    print("RELEASE CONTRACT REGRESSION: PASS")


if __name__ == "__main__":
    main()
