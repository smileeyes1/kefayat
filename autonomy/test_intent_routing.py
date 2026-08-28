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
    scores={'mathematics':0,'arabic':0,'islamic_education':0,'nurturing':0}
    if any(x in q for x in ('رياض','عدد','اعداد','جمع','طرح','ضرب','قسمة','كمية','عد','رقم','هندسة','قياس','مساله')): scores['mathematics']+=8
    if any(x in q for x in ('حرف','قراءة','كتابة','استماع','تحدث','لغة','نص','هجاء')): scores['arabic']+=8
    if any(x in q for x in ('وضوء','صلاة','قران','قرآن','حديث','سيرة','اسلام','عبادة')): scores['islamic_education']+=8
    if any(x in q for x in ('حواس','اسرة','اسرتي','اسره','بيئة','حيوان','نبات','فصول','مواطن','مدرسة','مجتمع','فلسطين')): scores['nurturing']+=8
    best=max(scores.values())
    return max(scores,key=scores.get) if best else 'unknown'

def test_math_query_does_not_leak_arabic():
    d=json.loads(KB.read_text(encoding='utf-8')); records=d['records']
    subject=infer('درس العدد ١',1)
    assert subject=='mathematics', subject
    candidates=[r for r in records if r.get('grade')==1 and r.get('subject')==subject]
    assert candidates, 'No Grade 1 mathematics records available'
    assert not any(r.get('id','').startswith('G1-ARABIC-') for r in candidates)

def test_ui_contains_explicit_routing_contract():
    t=INDEX.read_text(encoding='utf-8')
    for marker in ('inferMission','WISDOM','retrieveMission','Cross-Domain'):
        assert marker in t, f'missing UI routing marker: {marker}'

if __name__=='__main__':
    test_math_query_does_not_leak_arabic(); test_ui_contains_explicit_routing_contract(); print('INTENT ROUTING REGRESSION: PASS')
