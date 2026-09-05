# KEFAYAT / GEM Ω

## Evidence-Governed Educational Operating System

Kefayat Ω is an evidence-governed educational operating system whose primary service is to help teachers and the wider Palestinian educational community turn trusted knowledge, competencies, curricula, goals, and context into decisions and educational outputs that are executable, verifiable, traceable, and continuously improvable.

### Mission

`PURPOSE → CONTEXT → SOURCE → COMPETENCY → LEARNING OUTCOME → OBSERVABLE PERFORMANCE → ACTIVITY → EVIDENCE → ASSESSMENT → ASSURANCE → RELEASE → LEARNING`

### Operating principles

- Understand the real goal before execution.
- Prefer the most appropriate evidence over the first available information.
- Keep deterministic knowledge and assurance layers authoritative; AI is assistive and is not the curriculum oracle.
- Separate fact, evidence, inference, assumption, and claim scope.
- Fail closed when a material prerequisite is unproven.
- Execute → verify → attack the result → repair → regression-test → release.
- Convert discovered failures into permanent regression protection.
- Preserve human authority where judgment, safety, policy, or permissions require it.
- Optimize for correctness, evidence, relevance, safety, usability, maintainability, efficiency, traceability, and sustainability.

### Verified baseline control plane

Project authority no longer depends on one chat, Work session, or model runtime. The durable resume chain is:

`governance/verified-baseline-control-plane.md → state/verified-state.json → baselines/golden-render/contract.json → evidence → tests → CI → release decision`

A new executor must resume through `operating/BOOTSTRAP.md`, verify the persisted state, and continue from the last evidence-backed baseline rather than from a conversational claim.

The protected P0 Arabic math contract is:

`SEMANTIC / STUDENT-EYE: A + B = R`

`ENGINE REQUEST: R = B + A`

Reference: `٤ + ٣ = □` ⇐ engine request `□ = ٣ + ٤`.

Operand identities are immutable; RTL/BiDi is not the authority; the final rendered artifact seen by the learner is the acceptance oracle.

### Scope

- Grades 1–4 baseline
- Arabic
- Mathematics
- Islamic Education
- Nurturing / civic-life competencies
- Exact source preservation
- Separate normalization layer
- Stable IDs and traceability
- Grade progression and coverage audits
- Lesson and assessment generation
- MASTER Ω assurance gates
- Mathematical visual-order and graphics-count safeguards
- Islamic authenticity safeguards
- GitHub Pages as the canonical web deployment path

### Evidence posture

User-provided competency material is treated as `USER-PROVIDED REFERENCE` unless independently verified. The application must never silently promote user-provided content to `OFFICIAL VERIFIED SOURCE`.

Source-artifact Golden Render evidence is preserved within its stated verification scope. Platform-specific Gemini Gem acceptance remains `NOT_PROVEN` until an actual runtime fixture is observed; CI or source correctness must not be mislabeled as platform verification.

### Release posture

GitHub Actions is the canonical build, regression, and GitHub Pages deployment path. Vercel is not required for normal operation.

A successful build or deployment does not by itself prove field readiness. Production claims require the corresponding evidence, including runtime and field validation where applicable.

### Current baseline

The repository contains the autonomous control plane, structured competency build pipeline, protected verified-baseline control plane, Golden Render regression, adversarial autonomy regression, and conservative release-contract regression. GitHub Pages is configured to rebuild structured competency knowledge, run the release contract, upload the complete static artifact, and deploy it on changes to `main`.
