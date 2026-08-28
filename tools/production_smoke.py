from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
failures = []

def require(condition, message):
    if not condition:
        failures.append(message)

index = ROOT / "index.html"
manifest = ROOT / "manifest.webmanifest"
sw = ROOT / "sw.js"
knowledge = ROOT / "knowledge" / "competencies.json"

require(index.is_file() and index.stat().st_size > 0, "index.html missing or empty")
require(manifest.is_file() and manifest.stat().st_size > 0, "manifest.webmanifest missing or empty")
require(sw.is_file() and sw.stat().st_size > 0, "sw.js missing or empty")
require(knowledge.is_file() and knowledge.stat().st_size > 0, "knowledge/competencies.json missing or empty")

if index.exists():
    text = index.read_text(encoding="utf-8")
    require('<html lang="ar" dir="rtl">' in text, "Arabic RTL document contract missing")
    require("Evidence-Governed" in text, "Evidence-Governed product marker missing")
    require("Local-First" in text, "Local-First product marker missing")
    require("Self-Directed" in text, "Self-Directed product marker missing")
    require("kefayat.gemini.apiKey" in text, "local AI key storage contract missing")
    require("kefayat.gemini.dailyUsage" in text, "local usage governor contract missing")
    # Guard against the known mathematical visual-order regression in the UI source.
    require("٣ + ٤ = □" not in text and "3 + 4 = □" not in text, "forbidden mathematical visual order found in UI source")

if knowledge.exists():
    try:
        data = json.loads(knowledge.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "knowledge root must be an object")
        require(data.get("schema_version") == "1.0.0", "unexpected knowledge schema version")
        require(isinstance(data.get("records"), list), "knowledge records must be a list")
        require(isinstance(data.get("coverage"), list), "knowledge coverage must be a list")
        require(data.get("provenance_policy") == "USER-PROVIDED REFERENCE unless independently verified", "provenance policy changed unexpectedly")
        ids = [r.get("id") for r in data.get("records", []) if isinstance(r, dict)]
        require(len(ids) == len(set(ids)), "duplicate competency IDs detected")
        for r in data.get("records", []):
            if not isinstance(r, dict):
                failures.append("non-object competency record detected")
                continue
            require(r.get("provenance", {}).get("status") == "USER-PROVIDED REFERENCE", f"unsafe provenance promotion for {r.get('id')}")
    except Exception as exc:
        failures.append(f"invalid knowledge JSON: {exc}")

if failures:
    print("PRODUCTION_SMOKE: FAIL")
    for f in failures:
        print(f"- {f}")
    sys.exit(1)

print("PRODUCTION_SMOKE: PASS")
