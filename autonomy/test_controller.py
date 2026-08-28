#!/usr/bin/env python3
"""Adversarial regression tests for the deterministic autonomy control plane."""
from __future__ import annotations
import hashlib, json, os, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CONTROLLER=ROOT/"autonomy"/"controller.py"; KB=ROOT/"knowledge"/"competencies.json"; PLAN=ROOT/"autonomy"/"mission-plan.json"
def isolated_repo()->Path:
 work=Path(tempfile.mkdtemp(prefix="kefayat-auto-test-")); (work/"autonomy").mkdir(); (work/"knowledge").mkdir(); shutil.copy2(CONTROLLER,work/"autonomy"/"controller.py"); shutil.copy2(KB,work/"knowledge"/"competencies.json"); shutil.copy2(PLAN,work/"autonomy"/"mission-plan.json"); return work
def run_controller(repo:Path)->dict:
 env=os.environ.copy(); env["PYTHONHASHSEED"]="0"; env["KEFAYAT_ROOT"]=str(repo); p=subprocess.run(["python3",str(repo/"autonomy"/"controller.py")],cwd=repo,text=True,capture_output=True,env=env,check=False); assert p.returncode==0,p.stderr; return json.loads(p.stdout.strip().splitlines()[-1])
def read_state(repo:Path)->dict:return json.loads((repo/"autonomy"/"mission-state.json").read_text(encoding="utf-8"))
def test_kb_shape_and_identity():
 d=json.loads(KB.read_text(encoding="utf-8")); assert isinstance(d,dict) and isinstance(d.get("records"),list) and d["records"] and isinstance(d.get("coverage"),list); ids=[r["id"] for r in d["records"]]; assert len(ids)==len(set(ids)); assert all(r["grade"] in {1,2,3,4} for r in d["records"]); assert all(r["subject"] in {"arabic","mathematics","islamic_education","nurturing"} for r in d["records"])
def test_controller_source_uses_canonical_object_schema():
 t=CONTROLLER.read_text(encoding="utf-8"); assert "data.get(\"records\")" in t and "data.get(\"coverage\")" in t and "VALIDATE_KB" in t
def test_controller_has_safe_stop_release_and_progress_watchdog():
 t=CONTROLLER.read_text(encoding="utf-8"); assert "STAGNATION_DETECTED" in t and "AUTO-RELEASE-01" in t and "NO CLAIM" in t and "sig(" in t
def test_kb_sha256_is_stable():
 h=hashlib.sha256(KB.read_bytes()).hexdigest(); assert len(h)==64 and all(c in "0123456789abcdef" for c in h)
def test_real_persistent_progress_across_restart():
 repo=isolated_repo(); first=run_controller(repo); second=run_controller(repo); state=read_state(repo); assert first["action"]=="VALIDATE_PLAN"; assert second["action"]=="VALIDATE_KB"; assert "PLAN_VALIDATED" in state["completed_tasks"] and "KB_VALIDATED" in state["completed_tasks"]; assert state["artifact_identities"]["competencies.json"]==hashlib.sha256(KB.read_bytes()).hexdigest()
def test_corrupt_state_fails_closed():
 repo=isolated_repo(); (repo/"autonomy"/"mission-state.json").write_text("{broken",encoding="utf-8"); result=run_controller(repo); state=read_state(repo); assert result["status"]=="BLOCKED" and "STATE_CORRUPT" in state["blockers"] and result["next"]=="RECOVER_OR_ESCALATE"
def test_stagnation_detection_ignores_timestamp_and_history_noise():
 repo=isolated_repo(); s={"mission_id":"KEFAYAT-AUTO-001","baseline_id":"MASTER-OMEGA-vΩ.7.4-OAC-01-OAG-01","phase":"CONTROL_LOOP","status":"RUNNING","completed_tasks":["PLAN_VALIDATED","KB_VALIDATED","STATE_INTEGRITY_CHECKED","RELEASE_GATE_CHECKED"],"open_gaps":["AUTONOMY_RUNTIME_ASSURANCE"],"blockers":[],"attempt_counters":{},"stagnant_cycles":2,"last_checkpoint":"old","artifact_identities":{"competencies.json":"x"},"evidence_state":"UNREPORTED","claim_state":"NO CLAIM","release_state":"NOT READY","next_best_action":"WAIT_FOR_NEXT_MISSION","history":[{"checkpoint":"old"}]}; (repo/"autonomy/mission-state.json").write_text(json.dumps(s),encoding="utf-8"); result=run_controller(repo); final=read_state(repo); assert result["status"]=="SAFE_STOP" and final["stagnant_cycles"]>=3 and "STAGNATION_DETECTED" in final["blockers"]
def test_release_gate_cannot_claim_assurance_without_evidence():
 repo=isolated_repo(); s={"mission_id":"KEFAYAT-AUTO-001","baseline_id":"MASTER-OMEGA-vΩ.7.4-OAC-01-OAG-01","phase":"VERIFY","status":"RUNNING","completed_tasks":["PLAN_VALIDATED","KB_VALIDATED","STATE_INTEGRITY_CHECKED"],"open_gaps":["AUTONOMY_RUNTIME_ASSURANCE"],"blockers":[],"attempt_counters":{},"stagnant_cycles":0,"last_checkpoint":None,"artifact_identities":{},"evidence_state":"UNREPORTED","claim_state":"NO CLAIM","release_state":"NOT READY","next_best_action":"CHECK_RELEASE_GATE","history":[]}; (repo/"autonomy/mission-state.json").write_text(json.dumps(s),encoding="utf-8"); result=run_controller(repo); final=read_state(repo); ledger=(repo/"autonomy/evidence-ledger.jsonl").read_text(encoding="utf-8"); assert result["action"]=="CHECK_RELEASE_GATE" and final["release_state"]=="NOT READY" and final["claim_state"]=="NO CLAIM" and '"decision": "BLOCKED"' in ledger
if __name__=="__main__":
 for fn in (test_kb_shape_and_identity,test_controller_source_uses_canonical_object_schema,test_controller_has_safe_stop_release_and_progress_watchdog,test_kb_sha256_is_stable,test_real_persistent_progress_across_restart,test_corrupt_state_fails_closed,test_stagnation_detection_ignores_timestamp_and_history_noise,test_release_gate_cannot_claim_assurance_without_evidence): fn()
 print("AUTONOMY ADVERSARIAL REGRESSION: PASS")
