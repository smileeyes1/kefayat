#!/usr/bin/env python3
"""Release delivery contract: the production path must end in a directly reachable user-facing deployment."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / ".github" / "workflows" / "pages.yml"
CONTINUITY = ROOT / "autonomy" / "continuity_runner.py"


def main() -> None:
    pages = PAGES.read_text(encoding="utf-8")
    continuity = CONTINUITY.read_text(encoding="utf-8")

    required_pages_markers = (
        "actions/deploy-pages@v4",
        "steps.deployment.outputs.page_url",
        "curl --fail",
        "grep -q 'كفايات Ω'",
        "grep -q 'inferMission'",
        "grep -q 'WISDOM'",
        "grep -q 'القيادة الذاتية'",
    )
    for marker in required_pages_markers:
        assert marker in pages, f"delivery invariant missing: {marker}"

    required_continuity_markers = (
        "first unmet",
        "SAFE_STOP",
        "NO-GO",
        "evidence-ledger.jsonl",
    )
    for marker in required_continuity_markers:
        assert marker in continuity, f"continuity invariant missing: {marker}"

    print("DIRECT DELIVERY CONTRACT: PASS")


if __name__ == "__main__":
    main()
