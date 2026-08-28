#!/usr/bin/env python3
"""Hard release gate: prevents a final GO claim without the required evidence posture."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    required = [
        ROOT / 'README.md',
        ROOT / 'index.html',
        ROOT / 'knowledge' / 'competencies.json',
        ROOT / 'governance' / 'WISDOM_GOVERNANCE.md',
        ROOT / 'governance' / 'CONTINUITY_AND_COMPLETION_CONTRACT.md',
        ROOT / 'governance' / 'PROFESSIONAL_RELEASE_STANDARD.md',
        ROOT / 'quality' / 'test_production_contract.py',
        ROOT / 'quality' / 'test_release_contract.py',
        ROOT / 'autonomy' / 'test_intent_routing.py',
        ROOT / 'autonomy' / 'test_wisdom_governance.py',
    ]
    for p in required:
        assert p.exists() and p.stat().st_size > 0, f'missing release evidence: {p}'

    kb = json.loads((ROOT / 'knowledge' / 'competencies.json').read_text(encoding='utf-8'))
    records = kb.get('records')
    assert isinstance(records, list) and records, 'knowledge evidence missing'
    pairs = {(r.get('grade'), r.get('subject')) for r in records}
    for pair in ((1, 'arabic'), (1, 'mathematics'), (1, 'islamic_education'), (1, 'nurturing')):
        assert pair in pairs, f'coverage missing: {pair}'

    wisdom = (ROOT / 'governance' / 'WISDOM_GOVERNANCE.md').read_text(encoding='utf-8')
    continuity = (ROOT / 'governance' / 'CONTINUITY_AND_COMPLETION_CONTRACT.md').read_text(encoding='utf-8')
    professional = (ROOT / 'governance' / 'PROFESSIONAL_RELEASE_STANDARD.md').read_text(encoding='utf-8')
    for marker in ('evidence', 'human', 'stop', 'regression', 'proven'):
        assert marker.lower() in wisdom.lower(), f'wisdom contract marker missing: {marker}'
    for marker in ('continue', 'external blocker', 'system of record', 'release ladder'):
        assert marker.lower() in continuity.lower(), f'continuity contract marker missing: {marker}'
    for marker in ('BUILT', 'TESTED', 'DEPLOYED', 'RUNTIME-VERIFIED', 'FIELD-READY', 'Critical acceptance gates', 'Final GO rule'):
        assert marker.lower() in professional.lower(), f'professional release marker missing: {marker}'

    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    assert len(html) > 1000, 'application shell unexpectedly small'
    for marker in ('كفايات Ω', 'inferMission', 'القيادة الذاتية'):
        assert marker in html, f'critical UI marker missing: {marker}'

    print('GO GATE STRUCTURAL CONTRACT: PASS')


if __name__ == '__main__':
    main()
