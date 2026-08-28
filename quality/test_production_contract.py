#!/usr/bin/env python3
"""Production-contract checks that are safe to run before deployment."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
AI = ROOT / "ai.html"
MANIFEST = ROOT / "manifest.webmanifest"
SW = ROOT / "sw.js"
KB = ROOT / "knowledge" / "competencies.json"
RAW_NURTURING_1 = ROOT / "raw_sources" / "nurturing_grade_1.txt"


def main() -> None:
    for p, minimum in ((INDEX, 1000), (AI, 1000), (MANIFEST, 100), (SW, 500), (KB, 1000), (RAW_NURTURING_1, 500)):
        assert p.exists(), f"required artifact missing: {p}"
        assert p.stat().st_size >= minimum, f"required artifact too small: {p}"

    kb = json.loads(KB.read_text(encoding="utf-8"))
    records = kb.get("records")
    assert isinstance(records, list) and records, "knowledge records missing"

    required = {
        (1, "arabic"),
        (1, "mathematics"),
        (1, "islamic_education"),
        (1, "nurturing"),
    }
    present = {(r.get("grade"), r.get("subject")) for r in records}
    assert required <= present, f"Grade 1 subject coverage incomplete: missing={sorted(required-present)}"

    ids = [r.get("id") for r in records]
    assert all(ids) and len(ids) == len(set(ids)), "competency IDs must be present and unique"
    assert all(isinstance(r.get("provenance"), dict) and r["provenance"].get("status") for r in records), "provenance missing"
    assert all(isinstance(r.get("source_text"), str) and r["source_text"].strip() for r in records), "source text missing"

    ui = INDEX.read_text(encoding="utf-8")
    ai = AI.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    sw = SW.read_text(encoding="utf-8")

    for marker in ("inferMission", "retrieveMission", "wisdomGate", "Cross-Domain", "WISDOM", "localStorage"):
        assert marker in ui, f"core UI contract missing: {marker}"
    for marker in ("Gemini", "localStorage", "Free-First", "لا خادم مدفوع"):
        assert marker in ai, f"AI safety/free-first contract missing: {marker}"
    assert manifest.get("dir") == "rtl" and manifest.get("lang") == "ar", "manifest locale contract broken"
    assert "catch" in sw and "index.html" in sw, "offline fallback contract missing"

    print("PRODUCTION CONTRACT: PASS")


if __name__ == "__main__":
    main()
