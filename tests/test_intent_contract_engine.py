#!/usr/bin/env python3
"""Adversarial regression for KEFAYAT Ω intent-contract and fulfillment semantics."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'intent'/'intent-engine.js'
CONSTITUTION=ROOT/'governance'/'INTENT_FULFILLMENT_CONTRACT.md'


def run_node(source:str)->dict:
    p=subprocess.run(['node','-e',source],cwd=ROOT,text=True,capture_output=True,check=False)
    assert p.returncode==0, p.stderr
    return json.loads(p.stdout.strip())


def main()->None:
    assert ENGINE.is_file() and ENGINE.stat().st_size>5000
    assert CONSTITUTION.is_file() and CONSTITUTION.stat().st_size>1500
    text=ENGINE.read_text(encoding='utf-8')
    for marker in ('compileContract','retrieveEvidence','contractGate','buildPlan','acceptanceOracle','P0_GOLDEN_RENDER','PRESERVE_VERIFIED_BASELINES'):
        assert marker in text, marker

    js=r'''
const E=require('./intent/intent-engine.js');
const records=[
 {id:'G1-MATH-0001',grade:1,subject:'mathematics',main_competency:'الجمع',criterion:'الجمع ضمن ١٠',source_text:'يتعلم الطالب الجمع ضمن ١٠ باستخدام المحسوسات'},
 {id:'G2-MATH-0001',grade:2,subject:'mathematics',main_competency:'الجمع',criterion:'الجمع ضمن ١٨',source_text:'الجمع والطرح ضمن ١٨'},
 {id:'G2-ARABIC-0001',grade:2,subject:'arabic',main_competency:'القراءة',criterion:'قراءة نص',source_text:'قراءة نص قصير'}
];
const a=E.compileContract({text:'انشئ درس الجمع ضمن ١٠ كملف pdf'},records,{role:'teacher'});
const ar=E.retrieveEvidence(a,records);
const ag=E.contractGate(a,ar);
const ap=E.buildPlan(a,ar);
const blocked=E.acceptanceOracle(a,ar,{});
const passed=E.acceptanceOracle(a,ar,{actual_pdf_exists:true,actual_pdf_opens:true,all_pages_checked:true,student_eye_math_pass:true,eastern_digits_pass:true,equals_position_pass:true,print_pass:true,mobile_pass:true});
const b=E.compileContract({text:'حضّر درس قراءة للصف الثاني',subject:'arabic'},records,{role:'teacher'});
const c=E.compileContract({text:'اعمل درس'},[],{role:'teacher'});
const d=E.compileContract({text:'عدّل الملف دون كسر القاعدة المثبتة'},records,{role:'teacher'});
console.log(JSON.stringify({a,ar:ar.map(x=>x.id),ag,ap,blocked,passed,b,c,d}));
'''
    r=run_node(js)
    a=r['a']
    assert a['subject']=='mathematics', a
    assert a['grade']==1, a
    assert a['artifact_type']=='pdf' and a['task_type']=='lesson', a
    assert 'DELIVER_ACTUAL_PDF' in a['hard_requirements']
    assert 'P0_GOLDEN_RENDER' in a['hard_requirements']
    assert 'ENGINE_REQUEST_R_EQUALS_B_PLUS_A' in a['protected_invariants']
    assert r['ar'] and r['ar'][0]=='G1-MATH-0001', r
    assert r['ag']['pass'] is True, r
    assert 'BUILD_REAL_ARTIFACT' in r['ap']['steps'] and 'P0_GOLDEN_RENDER_QA' in r['ap']['steps']
    assert r['blocked']['decision']=='NOT_PROVEN' and 'ACTUAL_PDF_EXISTS' in r['blocked']['failed']
    assert r['passed']['decision']=='PASS', r['passed']
    assert r['b']['grade']==2 and r['b']['subject']=='arabic', r['b']
    assert r['c']['grade'] is None and 'grade' in r['c']['unresolved'], r['c']
    assert r['c']['subject'] is None, r['c']
    assert 'PRESERVE_VERIFIED_BASELINES' in r['d']['hard_requirements'] and 'NO_REGRESSION' in r['d']['hard_requirements'], r['d']

    gov=CONSTITUTION.read_text(encoding='utf-8')
    for marker in ('USER INTENT → INTENT CONTRACT','GENERATED` is never equivalent to `FULFILLED','actual PDF','٤ + ٣ = □','□ = ٣ + ٤','Zero-burden'):
        assert marker in gov, marker
    print('INTENT CONTRACT + FULFILLMENT REGRESSION: PASS')

if __name__=='__main__': main()
