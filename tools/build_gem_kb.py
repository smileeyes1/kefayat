from pathlib import Path
import re
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw_sources"
RAW.mkdir(exist_ok=True)

SOURCES = {
    "arabic": [
        (1, "كفايات اللغة العربية ومعاييرها للصف1. .docx"),
        (2, "كفايات اللغة العربية ومعاييرها للصف 2..docx"),
        (3, "كفايات اللغة العربية ومعاييرها للصف 3. .docx"),
        (4, "كفايات اللغة العربية ومعاييرها للصف 4..docx"),
    ],
    "math": [
        (1, "كفايات الرياضيات ومعاييرها للصف1.docx"),
        (2, "كفايات الرياضيات ومعاييرها للصف 2..docx"),
        (3, "كفايات الرياضيات ومعاييرها للصف 3.docx"),
        (4, "كفايات الرياضيات ومعاييرها للصف 4..docx"),
    ],
    "islamic": [
        (1, "كفايات التربية الاسلامية ومعاييرها للصف 1. .docx"),
        (2, "كفايات التربية الاسلامية ومعاييرها للصف 2. ا.docx"),
        (3, "كفايات التربية الاسلامية ومعاييرها للصف 3. docx.docx"),
        (4, "كفايات التربية الاسلامية ومعاييرها للصف 4. .docx"),
    ],
    "nurturing": [
        (1, "الكفايات والمعايبر والمؤشرات والقيم علوم وطنية وحياتية  اول (1.docx"),
        (2, "الكفايات والمعايبر والمؤشرات والقيم علوم وطنية وحياتية ثاني (1).docx"),
        (3, "كفايات التنشئة ومعاييرها للصف 3. .docx"),
        (4, "كفايات التنشئة ومعاييرها للصف 4. .docx"),
    ],
}


def norm(s):
    s = s.replace("\u00a0", " ").replace("\u200f", "").replace("\u200e", "")
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def extract_docx(path):
    doc = Document(path)
    blocks = []
    for p in doc.paragraphs:
        t = norm(p.text)
        if t:
            blocks.append(t)
    for ti, table in enumerate(doc.tables, 1):
        blocks.append(f"[TABLE {ti}]")
        for row in table.rows:
            cells = [norm(c.text).replace("\n", " / ") for c in row.cells]
            if any(cells):
                blocks.append(" | ".join(cells))
    return blocks


def build_subject(subject, items):
    out = [
        f"# GEM KNOWLEDGE BASE — {subject.upper()} — GRADES 1–4",
        "",
        "STATUS: GENERATED FROM USER-PROVIDED REFERENCE FILES IN THIS REPOSITORY.",
        "SOURCE CLASS: USER-PROVIDED REFERENCE; NOT CLAIMED OFFICIAL-VERIFIED.",
        "RULE: PRESERVE SOURCE TEXT; NORMALIZATION MUST NOT replace the raw source.",
        "TRACE: SOURCE → COMPETENCY → LEARNING OUTCOME → OBSERVABLE PERFORMANCE → ACTIVITY → EVIDENCE → ASSESSMENT.",
        "",
    ]
    for grade, filename in items:
        path = ROOT / filename
        if not path.exists():
            out += [f"## الصف {grade}", f"SOURCE FILE MISSING: `{filename}`", ""]
            continue
        blocks = extract_docx(path)
        raw_name = RAW / f"{subject}_grade_{grade}.txt"
        raw_name.write_text("\n".join(blocks) + "\n", encoding="utf-8")
        out += [f"## الصف {grade}", f"SOURCE: `{filename}`", "", "### ORIGINAL EXTRACTED TEXT", ""]
        out += blocks
        out += ["", "---", ""]
    return "\n".join(out) + "\n"

for subject, items in SOURCES.items():
    target = ROOT / f"GEM_KB_{subject.upper()}_GRADES_1-4.md"
    target.write_text(build_subject(subject, items), encoding="utf-8")

status = ROOT / "BASELINE_EXTRACTION_STATUS.md"
status.write_text(
    "# BASELINE EXTRACTION STATUS\n\n"
    "Generated automatically from the repository DOCX sources.\n\n"
    "All extracted text is retained under `raw_sources/`; subject KBs retain the extracted text grouped by grade.\n"
    "The nurturing grade 1–2 files are the repository's `علوم وطنية وحياتية` sources; this mapping is explicitly preserved and must not be presented as independently verified equivalence.\n",
    encoding="utf-8",
)
