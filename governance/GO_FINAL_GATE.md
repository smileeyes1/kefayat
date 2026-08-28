# Kafayat Ω — Final Production GO Gate

## Purpose
A release is GO only when every critical acceptance gate passes. A successful build or deployment alone is insufficient.

## Gate order
1. PURPOSE — mission and supported roles are explicit.
2. KNOWLEDGE — required knowledge sources exist, are traceable, and carry provenance/verification state.
3. INTENT — request intent, domain, grade, role, and context are resolved before retrieval.
4. RETRIEVAL — evidence is constrained to the resolved scope; cross-domain contamination is blocked.
5. WISDOM — alternatives, risks, evidence sufficiency, proportionality, and human-judgment boundaries are considered.
6. EXECUTION — output is actionable and respects permissions and constraints.
7. ASSURANCE — output is structurally and semantically checked.
8. ADVERSARIAL — tests actively seek wrong-domain, stale, missing, conflicting, hallucinated, corrupted, and unsafe outcomes.
9. REPAIR — recoverable failures are fixed and retested.
10. REGRESSION — every fixed critical failure has a permanent regression test.
11. RELEASE — build, packaging, deployment and rollback paths are reproducible.
12. RUNTIME — deployed runtime is directly verified for core journeys.
13. FIELD — real-world pilot evidence exists before claiming field readiness.

## Mandatory critical tests
- `درس العدد ١` resolves to Grade 1 Mathematics, not Arabic.
- `درس الحواس الخمس` resolves to the appropriate Grade 1 educational domain, not Mathematics.
- Unknown/ambiguous requests do not receive fabricated references.
- Knowledge corruption causes a safe failure rather than silent degradation.
- AI output cannot bypass domain, evidence, permission, or safety gates.
- Failed execution cannot silently be reported as successful.

## Evidence levels
`BUILT < TESTED < DEPLOYED < RUNTIME_VERIFIED < FIELD_PILOT < FIELD_READY`

Never promote a claim above the highest evidence level actually demonstrated.

## Decision
- **GO:** all critical gates PASS and no critical defect is open.
- **CONDITIONAL GO:** product works within a clearly documented limited scope, with non-critical evidence gaps.
- **NO-GO:** any critical gate fails, evidence is insufficient for a critical claim, or a critical defect remains open.

## Non-negotiable rule
No success claim may be based solely on code presence, CI green status, or deployment success. Runtime and field claims require corresponding runtime and field evidence.
