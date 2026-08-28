from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
html = (root / 'index.html').read_text(encoding='utf-8')
kb = json.loads((root / 'knowledge/competencies.json').read_text(encoding='utf-8'))

assert '<html lang="ar" dir="rtl">' in html, 'Arabic RTL document root missing'
assert "./knowledge/competencies.json" in html, 'KB endpoint missing'
assert 'Array.isArray(data.records)' in html, 'KB records guard missing'
assert 'provenance' in html and 'source_text' in html, 'provenance/source UI missing'
assert 'MASTER Ω' in html, 'assurance identity missing'
assert 'No claim' in html or 'Claim' in html, 'claim guard messaging missing'
assert 'cache:' in html, 'deterministic cache policy missing'
assert '<script>' in html and '</script>' in html, 'runtime script missing'
assert not re.search(r'https?://(?!schema\.org)', html), 'unexpected external runtime URL detected'
assert isinstance(kb, dict) and isinstance(kb.get('records'), list), 'KB shape invalid'
assert len(kb['records']) > 0, 'KB empty'

print(f'UI smoke: PASS ({len(kb["records"])} records wired)')
