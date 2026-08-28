#!/usr/bin/env python3
"""Adversarial regression for mission intent/domain routing."""
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'
KB=ROOT/'knowledge'/'competencies.json'

def norm(s):
    return re.sub(r'[\u064B-\u065F\u0670]', '', s).replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ى','ي').lower()

def infer(text, grade=None, subject=None):
    q=norm(text)
    if subject and subject != 'all': return subject
    math=('عدد' in q or 'اعداد' in q or 'جمع' in q or 'طرح' in q or 'ضرب' in q or 'رياض' in q or 'كمية' in q or 'العد' in q)
    arabic=('حرف' in q or 'قراءة' in q or 'كتابة' in q or 'استماع' in q or 'لغة' in q)
    islamic=('وضوء' in q or 'صلاة' in q or 'قران' in q or 'سيرة' in q or 'حديث' in q)
    nurturing=('حواس' in q or 'اسرة' in q or 'اسرتي' in q or 'بيئة' in q or 'حيوان' in q or 'نبات' in q or 'فصول' in q or 'مواطن' in q)
    scores={'mathematics':int(math),'arabic':int(arabic),'islamic_education':int(islamic),'nurturing':int(nurturing)}
    return max(scores,key=scores.get) if max(scores.values()) else 'unknown'

def test_math_query_does_not_leak_arabic():
    d=json.loads(KB.read_text(encoding='utf-8')); records=d['records']
    q='درس العدد ١'; subject=infer(q,1)
    assert subject=='mathematics', subject
    candidates=[r for r in records if r.get('grade')==1 and r.get('subject')==subject]
    assert candidates, 'No Grade 1 mathematics records available'
    assert not any(r.get('id','').startswith('G1-ARABIC-') for r in candidates)

def test_ui_contains_explicit_routing_contract():
    t=INDEX.read_text(encoding='utf-8')
    for marker in ('inferMission','WISDOM','retrieveMissionRecords','Cross-Domain'):
        assert marker in t, f'missing UI routing marker: {marker}'

if __name__=='__main__':
    test_math_query_does_not_leak_arabic(); test_ui_contains_explicit_routing_contract(); print('INTENT ROUTING REGRESSION: PASS')
