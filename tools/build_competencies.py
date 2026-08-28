from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw_sources"
OUT = ROOT / "knowledge" / "competencies.json"

FILES = {
    "arabic": [1, 2, 3, 4],
    "mathematics": [1, 2, 3, 4],
    "islamic_education": [1, 2, 3, 4],
    "nurturing": [1, 2, 3, 4],
}

RAW_SUBJECT = {
    "arabic": "arabic",
    "mathematics": "math",
    "islamic_education": "islamic",
    "nurturing": "nurturing",
}


def clean(s):
    s = s.replace("\u00a0", " ").replace("\u200f", "").replace("\u200e", "")
    return re.sub(r"\s+", " ", s).strip()


def stable_id(grade, subject, n):
    return f"G{grade}-{subject.upper()}-{n:04d}"


def parse_file(path, grade, subject):
    if not path.exists():
        return [], {"status": "MISSING", "path": str(path.relative_to(ROOT))}
    text = path.read_text(encoding="utf-8")
    lines = [clean(x) for x in text.splitlines() if clean(x)]
    records = []
    for line in lines:
        if line.startswith("[TABLE"):
            continue
        if " | " not in line:
            continue
        cells = [clean(x) for x in line.split(" | ")]
        # Supported source shapes:
        # 7+ cells: domain, main, sub, criterion, outcomes, mastery x3, optional values.
        # 6 cells (Islamic Education): main, sub, criterion, mastery x3.
        if subject == "islamic_education" and len(cells) >= 6:
            if cells[0] in {"الكفايات الرئيسة", "المجال"}:
                continue
            domain, main, sub, criterion = None, cells[0], cells[1], cells[2]
            mastery = {"يتقن": cells[3], "يطور": cells[4], "يحاول": cells[5]}
            outcome = None
        else:
            if len(cells) < 7:
                continue
            if cells[0] in {"المجال", "المجال المعرفي"} or cells[3] in {"المعايير", "المعيار"}:
                continue
            domain, main, sub, criterion = cells[0], cells[1], cells[2], cells[3]
            # For standard 7-column sources, cells 4+ contain outcome/mastery/values.
            # Keep the original row untouched for traceability.
            outcome = cells[4] if len(cells) >= 8 else None
            mastery = {"يتقن": cells[-3], "يطور": cells[-2], "يحاول": cells[-1]}

        rec = {
            "id": stable_id(grade, subject, len(records) + 1),
            "grade": grade,
            "subject": subject,
            "domain": domain or None,
            "main_competency": main or None,
            "sub_competency": sub or None,
            "criterion": criterion or None,
            "learning_outcomes": [outcome] if outcome else [],
            "mastery_levels": mastery,
            "values": [],
            "provenance": {
                "status": "USER-PROVIDED REFERENCE",
                "source_id": path.name,
                "location": f"raw_sources/{path.name}"
            },
            "source_text": line,
            "normalized": None,
            "source_row": cells
        }
        records.append(rec)
    return records, {"status": "PARSED", "path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size}


records = []
coverage = []
for subject, grades in FILES.items():
    for grade in grades:
        p = RAW / f"{RAW_SUBJECT[subject]}_grade_{grade}.txt"
        rows, meta = parse_file(p, grade, subject)
        records.extend(rows)
        coverage.append({"grade": grade, "subject": subject, **meta, "records": len(rows)})

status = "COMPLETE_STRUCTURAL_PARSE" if all(x["status"] == "PARSED" for x in coverage) else "INCOMPLETE_SOURCE_COVERAGE"
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({
    "schema_version": "1.2.0",
    "status": status,
    "provenance_policy": "USER-PROVIDED REFERENCE unless independently verified",
    "records": records,
    "coverage": coverage,
    "rule": "No missing competency text is invented. Source text is preserved per record; normalization is separate."
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Generated {len(records)} structured records; status={status}")
