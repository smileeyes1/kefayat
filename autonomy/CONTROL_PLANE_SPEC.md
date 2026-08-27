# KEFAYAT / GEM Ω — Autonomous Control Plane

## Mission
Provide autonomous, resumable, evidence-governed execution toward the professional application release gate while preserving human authority over non-delegable decisions.

## Core loop
UNDERSTAND → EXTRACT → INTEGRITY → FREEZE → PLAN → EXECUTE → VERIFY → BREAK → REPAIR → REVERIFY → REGRESSION → EVIDENCE AUDIT → CLAIM-SCOPE → DECIDE → CONTINUE/RELEASE/ESCALATE

## Persistent state
The controller MUST persist mission state, queue, checkpoints, blockers, decisions, artifact identifiers, evidence state, and release state. Restart behavior MUST validate the last checkpoint and resume safely rather than blindly restarting.

## Decision engine
After every meaningful state transition, compute candidate actions from open requirements, dependencies, risk, evidence gaps, blockers, and mission value. Select the highest-value safe action that is within delegated authority.

## Safety controls
- Idempotent operations where practical.
- Bounded retries and execution budgets.
- Loop, deadlock, and stagnation detection.
- Snapshot before consequential mutation.
- Automatic rollback when post-change validation fails.
- No self-approval of generated artifacts.
- AI output is untrusted until validated.
- Critical blockers prevent release.

## Authority model
AUTONOMOUS: discovery, extraction, normalization, deterministic validation, test execution, evidence collection, safe repair, regression, documentation, packaging, and resumable continuation.

ESCALATE: conflicting authoritative requirements, missing authoritative evidence where invention would be required, irreversible high-impact external actions, credential/authorization decisions, and genuinely non-delegable human policy decisions.

## Assurance separation
Generator ≠ Oracle ≠ Verifier ≠ Evidence Auditor ≠ Release Judge whenever practical. Internal automation must never be presented as external independence.

## Evidence and claims
Every material claim must map to requirement, test, artifact, method, observed result, evidence, scope, and decision. Evidence state may only escalate through defined transition criteria. No broad claim from narrow evidence.

## Curriculum controls
Official competency sources remain source-of-truth inputs. Preserve provenance and source text. Track grade, subject, domain, competency, outcome, performance, prerequisite, activity, assessment, and evidence relationships. Detect gaps, duplicates, broken prerequisites, and coverage failures.

## Islamic education controls
Religious claims require source/provenance and authenticity checks appropriate to the claim. The system MUST NOT invent quotations, hadith attribution, rulings, or source details to fill gaps. Unresolved high-risk claims are blocked or escalated.

## Mathematical and visual controls
Mathematical order is explicit, never inferred from RTL/BiDi/CSS/DOM/renderers. For every numeric visual: VALUE → REQUIRED COUNT → VISUAL GROUP → ACTUAL COUNT → EVIDENCE. A critical mismatch is NO-GO.

## Release posture
The controller may continue autonomously while safe, valuable work remains. It releases only after the applicable release gate passes. It stops/escalates on hard blockers, non-delegable decisions, exhausted safe recovery paths, or mission completion.

## Non-goals
This specification does not claim uninterrupted operation forever, universal validity, external independence, or immunity from failure. Those claims require separate evidence.
