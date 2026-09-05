#!/usr/bin/env python3
"""Behavioral adversarial regression for the Kefayat Ω control plane."""
from __future__ import annotations
import hashlib, json, os, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CONTROLLER=ROOT/"autonomy"/"controller.py"; KB=ROOT/"knowledge"/"competencies.json"; PLAN=ROOT/"autonomy"/"mission-plan.json"
EXTRA=[
 "state/verified-state.json","baselines/golden-render/contract.json","governance/verified-baseline-control-plane.md",
 "GEM_KNOWLEDGE_PACK/02_MATH_VISUAL_CONSTITUTION.md","evidence/imported/Ω_GOLDEN_RENDER_TEST_SUITE_v1.0.md","evidence/imported/Ω_RELEASE_EVIDENCE_v4.2.txt"
]
def isolated_repo():
    work=Path(tempfile.mkdtemp(prefix="kefayat-auto-test-")); (work/"autonomy").mkdir(parents=True); (work/"knowledge").mkdir(parents=True); shutil.copy2(CONTROLLER,work/"autonomy"/"controller.py"); shutil.copy2(KB,work/"knowledge"/"competencies.json"); shutil.copy2(PLAN,work/"autonomy"/"mission-plan.json")
    for rel in EXTRA:
        src=ROOT/rel; dst=work/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    return work
def run_controller(repo):
    env=os.environ.copy(); env["PYTHONHASHSEED"]="0"; env["KEFAYAT_ROOT"]=str(repo); p=subprocess.run(["python3",str(repo/"autonomy"/"controller.py")],cwd=repo,text=True,capture_output=True,env=env,check=False); assert p.returncode==0,p.stderr; return json.loads(p.stdout.strip().splitlines()[-1])
def read_state(repo): return json.loads((repo/"autonomy/mission-state.json").read_text(encoding="utf-8"))
def write_state(repo,s): (repo/"autonomy/mission-state.json").write_text(json.dumps(s,ensure_ascii=False),encoding="utf-8")
def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def bootstrap_to_baseline(repo):
    results=[run_controller(repo) for _ in range(4)]; state=read_state(repo); assert results[-1]["action"]=="VALIDATE_BASELINE_CONTROL_PLANE",results; assert "BASELINE_CONTROL_PLANE_VALIDATED" in state["completed_tasks"],state; assert state["artifact_identities"].get("control_plane_fingerprint"),state; return state

def test_kb_shape_and_identity():
    d=json.loads(KB.read_text(encoding="utf-8")); assert isinstance(d,dict) and d.get("records") and isinstance(d.get("coverage"),list); ids=[r["id"] for r in d["records"]]; assert len(ids)==len(set(ids)); assert all(r["grade"] in {1,2,3,4} for r in d["records"]); assert all(r["subject"] in {"arabic","mathematics","islamic_education","nurturing"} for r in d["records"])
def test_progress_and_identity_behavior():
    repo=isolated_repo(); first=run_controller(repo); second=run_controller(repo); state=read_state(repo); expected=sha256(repo/"knowledge/competencies.json"); assert first["action"]=="VALIDATE_PLAN",first; assert second["action"]=="VALIDATE_KB",second; assert "PLAN_VALIDATED" in state["completed_tasks"]; assert "KB_VALIDATED" in state["completed_tasks"]; assert state["artifact_identities"].get("competencies.json")==expected,state
def test_controller_controls_exist():
    t=CONTROLLER.read_text(encoding="utf-8"); assert "STAGNATION_DETECTED" in t and "AUTO-RELEASE-01" in t and "NOT_PROVEN" in t and "VALIDATE_BASELINE_CONTROL_PLANE" in t and "IDLE_SAFE_STOP" in t and "sig(" in t
def test_kb_sha256_is_stable():
    h=sha256(KB); assert len(h)==64 and all(c in "0123456789abcdef" for c in h)
def test_corrupt_state_fails_closed():
    repo=isolated_repo(); (repo/"autonomy/mission-state.json").write_text("{broken",encoding="utf-8"); result=run_controller(repo); state=read_state(repo); assert result["status"]=="BLOCKED" and "STATE_CORRUPT" in state["blockers"] and result["next"]=="RECOVER_OR_ESCALATE"
def test_verified_baseline_validation():
    repo=isolated_repo(); state=bootstrap_to_baseline(repo); assert state["evidence_state"]=="VERIFIED_SOURCE_SCOPE"; assert len(state["artifact_identities"]["control_plane_fingerprint"])==64
def test_stagnation_detection_and_idle_no_churn():
    repo=isolated_repo(); s=bootstrap_to_baseline(repo); s["completed_tasks"].append("RELEASE_GATE_CHECKED"); s["status"]="RUNNING"; s["stagnant_cycles"]=2; s["next_best_action"]="WAIT_FOR_NEXT_MISSION"; write_state(repo,s); result=run_controller(repo); final=read_state(repo); assert result["status"]=="SAFE_STOP" and final["stagnant_cycles"]>=3 and "STAGNATION_DETECTED" in final["blockers"]
    before=sha256(repo/"autonomy/mission-state.json"); idle=run_controller(repo); after=sha256(repo/"autonomy/mission-state.json"); assert idle["action"]=="IDLE_SAFE_STOP" and before==after,(idle,before,after)
def test_new_control_plane_reopens_stagnation():
    repo=isolated_repo(); s=bootstrap_to_baseline(repo); s["completed_tasks"].append("RELEASE_GATE_CHECKED"); s["status"]="SAFE_STOP"; s["blockers"]=["STAGNATION_DETECTED"]; s["artifact_identities"]["control_plane_fingerprint"]="0"*64; s["stagnant_cycles"]=9; write_state(repo,s); result=run_controller(repo); final=read_state(repo); assert result["action"]=="VALIDATE_BASELINE_CONTROL_PLANE",result; assert result["status"]=="RUNNING",result; assert "STAGNATION_DETECTED" not in final["blockers"]; assert "RELEASE_GATE_CHECKED" not in final["completed_tasks"]
def test_release_gate_blocks_unproven_runtime_claim():
    repo=isolated_repo(); s=bootstrap_to_baseline(repo); s["status"]="RUNNING"; s["completed_tasks"]=[x for x in s["completed_tasks"] if x!="RELEASE_GATE_CHECKED"]; s["next_best_action"]="CHECK_RELEASE_GATE"; write_state(repo,s); result=run_controller(repo); final=read_state(repo); ledger=(repo/"autonomy/evidence-ledger.jsonl").read_text(encoding="utf-8"); assert result["action"]=="CHECK_RELEASE_GATE"; assert final["release_state"]=="CONTROL_PLANE_READY__PLATFORM_RUNTIME_NOT_PROVEN"; assert "PLATFORM RUNTIME NOT PROVEN" in final["claim_state"] and '"decision": "BLOCKED"' in ledger
if __name__=="__main__":
    for fn in (test_kb_shape_and_identity,test_progress_and_identity_behavior,test_controller_controls_exist,test_kb_sha256_is_stable,test_corrupt_state_fails_closed,test_verified_baseline_validation,test_stagnation_detection_and_idle_no_churn,test_new_control_plane_reopens_stagnation,test_release_gate_blocks_unproven_runtime_claim): fn()
    print("AUTONOMY ADVERSARIAL REGRESSION: PASS")
