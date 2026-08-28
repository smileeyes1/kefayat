from dataclasses import dataclass
from enum import Enum


class EvidenceLevel(str, Enum):
    BUILT = "BUILT"
    TESTED = "TESTED"
    DEPLOYED = "DEPLOYED"
    RUNTIME_VERIFIED = "RUNTIME_VERIFIED"
    FIELD_PILOT = "FIELD_PILOT"
    FIELD_READY = "FIELD_READY"


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    evidence: str
    critical: bool = True


@dataclass(frozen=True)
class ReleaseDecision:
    status: str
    highest_evidence: EvidenceLevel
    failed_critical: tuple[str, ...]
    missing_critical: tuple[str, ...]


def evaluate_gates(results: list[GateResult], claimed_level: EvidenceLevel) -> ReleaseDecision:
    failed = tuple(r.name for r in results if r.critical and not r.passed)
    missing = tuple(r.name for r in results if r.critical and not r.evidence)
    if failed or missing:
        return ReleaseDecision("NO-GO", EvidenceLevel.BUILT, failed, missing)
    # Evidence is deliberately supplied by the caller from actual verification;
    # this function never upgrades evidence merely because CI/deployment succeeded.
    ordered = list(EvidenceLevel)
    highest = max((claimed_level,), key=ordered.index)
    return ReleaseDecision("GO", highest, (), ())


def require_runtime_for_runtime_claim(decision: ReleaseDecision) -> None:
    if decision.status == "GO" and decision.highest_evidence in {
        EvidenceLevel.RUNTIME_VERIFIED,
        EvidenceLevel.FIELD_PILOT,
        EvidenceLevel.FIELD_READY,
    }:
        return
    if decision.highest_evidence in {EvidenceLevel.BUILT, EvidenceLevel.TESTED, EvidenceLevel.DEPLOYED}:
        raise RuntimeError("NO-GO for runtime/field claim: direct runtime evidence is missing")
