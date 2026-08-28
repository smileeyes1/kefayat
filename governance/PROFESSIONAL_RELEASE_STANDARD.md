# كفايات Ω — Professional Release Standard

## Purpose
This standard defines the minimum evidence required before calling a build a production-ready release. It prevents confusing source completeness, CI success, deployment success, and real-world readiness.

## Release ladder
1. **BUILT** — required source files and build steps exist.
2. **TESTED** — automated structural, governance, intent, autonomy, and adversarial tests pass.
3. **DEPLOYED** — the selected production channel reports a successful deployment.
4. **RUNTIME-VERIFIED** — the deployed URL responds and critical application markers are present.
5. **OPERATIONALLY-READY** — recovery, continuity, bounded autonomy, data integrity, and release controls are present.
6. **FIELD-READY** — a defined pilot confirms the product works in the declared real-world scope.

A level must never be claimed unless its evidence exists.

## Professional acceptance principles
- Purpose before implementation.
- Evidence before claim.
- Explicit domain/grade/role routing before retrieval.
- Source provenance and traceability for knowledge.
- Human authority remains intact for decisions requiring human judgment or authorization.
- Autonomous execution is bounded by stop, escalation, and recovery rules.
- Every critical failure becomes a regression test or protective control.
- Prefer deterministic/local processing when it provides the required result; use AI when it adds material value.
- No secret, credential, or privileged token is committed to the repository.
- Release artifacts are reproducible from the system of record.
- Production claims are scoped; no absolute-correctness or unlimited-service claim is permitted.

## Critical acceptance gates
### Knowledge
- Knowledge build succeeds.
- Records are structured and non-empty.
- Grade/subject coverage required by the declared release exists.
- User-provided material is not silently represented as official source material.

### Intent and retrieval
- Role, grade, subject, and mission are resolved before retrieval when inferable.
- Cross-domain contamination is blocked.
- `درس العدد ١` resolves to first-grade mathematics and does not return Arabic listening competencies as the primary domain.
- Ambiguous or unsupported requests fail safely rather than fabricating evidence.

### Governance and autonomy
- Wisdom Governance regression passes.
- Autonomous controller has explicit safe-stop, no-claim, recovery/escalation behavior.
- Completion contract prevents unnecessary user hand-offs between executable steps.

### Product quality
- Production and release contract tests pass.
- Critical UI assets are present and non-empty.
- Arabic RTL requirements are preserved.
- Mathematical visual order is explicit where mathematical visuals are used; rendering direction must not redefine educational order.
- Numerical visuals must satisfy VALUE → REQUIRED COUNT → VISUAL GROUP and be count-verified.

### Deployment
- CI passes on the exact release commit.
- GitHub Pages deployment succeeds.
- Runtime smoke test reaches the deployed URL and verifies critical application markers.

### Operational safety
- Failure and recovery paths are defined.
- No known critical defect blocks the declared release scope.
- Known limitations are documented.
- A rollback/recovery path exists for the deployment channel.

## Final GO rule
**GO** is allowed only when all critical gates above pass on the same release candidate and the evidence is traceable to the exact commit/deployment.

Otherwise the status is **NO-GO** or **CONDITIONAL GO**, with the missing evidence explicitly stated.

## What GO does not mean
GO does not mean perfect, infallible, universally applicable, or permanently failure-free. It means the release candidate is professionally acceptable for the explicitly declared scope, with no known critical blocker and with evidence supporting the claims made about it.
