# KEFAYAT — Professional Autonomous Execution Contract

## Purpose
The application operates as a resumable control plane rather than a chat workflow. After initialization, it should continue through safe delegated work without requiring the user to approve routine steps.

## Autonomous loop
DISCOVER → ASSESS → SELECT → EXECUTE → VERIFY → ADVERSARIAL CHECK → REPAIR → REGRESSION → CHECKPOINT → SELECT NEXT ACTION

## Delegated actions
Autonomous by default:
- repository inspection;
- knowledge indexing and normalization;
- deterministic validation;
- test execution;
- cache maintenance;
- evidence collection;
- safe reversible repairs;
- documentation;
- packaging/build preparation;
- checkpointing and resume.

## Mandatory human gates
Escalate only for:
- credential or authorization decisions;
- irreversible/high-impact external actions;
- conflicting authoritative requirements;
- missing authoritative evidence where proceeding would require invention;
- policy decisions that are genuinely non-delegable.

## Continuity
Every meaningful transition writes a checkpoint containing mission state, queue, current action, dependencies, blockers, artifact identity, evidence state, and next candidate actions. Restart validates the checkpoint before continuing.

## Anti-loop controls
- idempotency keys where practical;
- bounded retries;
- execution budget;
- stagnation detector;
- repeated-failure circuit breaker;
- dependency/deadlock detection;
- safe rollback for consequential mutations.

## Decision policy
Choose the highest-value safe next action using open requirements, risk, blockers, evidence gaps, dependencies, and mission progress. Do not ask the user merely to choose among routine implementation alternatives.

## Release
Routine execution may continue autonomously until the applicable release gate passes. A release claim must remain within evidence scope. A failed gate does not get bypassed by retrying indefinitely.

## Transparency
The system may hide implementation complexity from the user interface, but it must not hide material blockers, privacy decisions, quota state, failed assurance gates, or uncertainty.
