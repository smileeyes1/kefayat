import pytest

from autonomy.go_final_gate import EvidenceLevel, GateResult, evaluate_gates, require_runtime_for_runtime_claim


def test_critical_failure_is_no_go():
    decision = evaluate_gates([
        GateResult("intent", False, "wrong-domain regression"),
        GateResult("knowledge", True, "knowledge build"),
    ], EvidenceLevel.TESTED)
    assert decision.status == "NO-GO"
    assert "intent" in decision.failed_critical


def test_missing_evidence_is_no_go():
    decision = evaluate_gates([
        GateResult("runtime", True, ""),
    ], EvidenceLevel.DEPLOYED)
    assert decision.status == "NO-GO"
    assert "runtime" in decision.missing_critical


def test_runtime_claim_cannot_be_made_from_deployment_only():
    decision = evaluate_gates([
        GateResult("build", True, "CI"),
        GateResult("deploy", True, "Pages"),
    ], EvidenceLevel.DEPLOYED)
    with pytest.raises(RuntimeError):
        require_runtime_for_runtime_claim(decision)


def test_runtime_evidence_allows_runtime_claim():
    decision = evaluate_gates([
        GateResult("runtime", True, "direct runtime verification"),
    ], EvidenceLevel.RUNTIME_VERIFIED)
    assert decision.status == "GO"
    require_runtime_for_runtime_claim(decision)
