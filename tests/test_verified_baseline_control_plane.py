#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'baselines/golden-render/contract.json'
STATE=ROOT/'state/verified-state.json'
AUTH=ROOT/'governance/verified-baseline-control-plane.md'
MATH=ROOT/'GEM_KNOWLEDGE_PACK/02_MATH_VISUAL_CONSTITUTION.md'
OLD_MASTER=ROOT/'GEM_KNOWLEDGE_PACK/KEFAYAT_OMEGA_MASTER_KNOWLEDGE_AR.md'
NEW_MASTER=ROOT/'GEM_KNOWLEDGE_PACK/KEFAYAT_OMEGA_MASTER_KNOWLEDGE_AR_v2.md'
GOLDEN=ROOT/'evidence/imported/Ω_GOLDEN_RENDER_TEST_SUITE_v1.0.md'
RELEASE=ROOT/'evidence/imported/Ω_RELEASE_EVIDENCE_v4.2.txt'
EASTERN=set('٠١٢٣٤٥٦٧٨٩')

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()

def main()->None:
    for p in (CONTRACT,STATE,AUTH,MATH,OLD_MASTER,NEW_MASTER,GOLDEN,RELEASE):
        assert p.is_file() and p.stat().st_size>0, f'missing/empty: {p}'
    c=json.loads(CONTRACT.read_text(encoding='utf-8'))
    assert c['severity']=='P0' and c['status']=='PROTECTED'
    assert c['semantic_pattern']=='A + B = R'
    assert c['engine_pattern']=='R = B + A'
    assert c['operand_identity_immutable'] is True
    assert c['commutativity_allows_swap'] is False
    assert c['rtl_bidi_is_authority'] is False
    ids=set()
    for f in c['fixtures']:
        assert f['id'] not in ids; ids.add(f['id'])
        expected_engine=f"{f['r']} = {f['b']} + {f['a']}"
        expected_eye=f"{f['a']} + {f['b']} = {f['r']}"
        assert f['engine']==expected_engine, (f,expected_engine)
        assert f['student_eye']==expected_eye, (f,expected_eye)
        digits={ch for ch in f['engine']+f['student_eye'] if ch.isdigit()}
        assert digits <= EASTERN, (f,digits)
    g01=c['fixtures'][0]
    assert g01['engine']=='□ = ٣ + ٤'
    assert g01['student_eye']=='٤ + ٣ = □'
    assert g01['student_eye']!='٣ + ٤ = □'
    math=MATH.read_text(encoding='utf-8')
    assert 'TARGET/USER-EYE: ٤ + ٣ = □' in math
    assert 'ENGINE REQUEST: □ = ٣ + ٤' in math
    assert 'Therefore the human-visible result must be exactly:\n`□ = ٤ + ٣`' not in math
    old=OLD_MASTER.read_text(encoding='utf-8')
    assert 'DEPRECATED RETRIEVAL STUB' in old and 'do not use this file as active mathematical authority'.lower() in old.lower()
    new=NEW_MASTER.read_text(encoding='utf-8')
    assert 'ENGINE □ = ٣ + ٤' in new and 'USER-EYE ٤ + ٣ = □' in new
    s=json.loads(STATE.read_text(encoding='utf-8'))
    assert s['golden_render']['gemini_runtime_acceptance']=='NOT_PROVEN'
    assert s['claim_scope']['source_artifact_golden_render']=='VERIFIED_SOURCE'
    assert s['current_source']['status']=='CANDIDATE_RC_NOT_RUNTIME_QUALIFIED'
    assert sha(GOLDEN)==s['golden_render']['source_suite_sha256']
    assert sha(RELEASE)==s['golden_render']['release_evidence_sha256']
    auth=AUTH.read_text(encoding='utf-8')
    for needle in ('CANDIDATE','VERIFIED_SOURCE','VERIFIED_RUNTIME','REJECTED','A + B = R','R = B + A','NOT_PROVEN'):
        assert needle in auth, needle
    assert not re.search(r'(?<![A-Za-z])4\s*\+\s*3\s*=\s*□', g01['student_eye'])
    print('VERIFIED BASELINE CONTROL PLANE: PASS')

if __name__=='__main__': main()
