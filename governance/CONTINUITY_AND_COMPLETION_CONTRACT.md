# KEFAYAT Ω — CONTINUITY & COMPLETION CONTRACT

## Purpose
This contract makes the repository the durable source of truth for the mission. Work must not depend on chat history, a single conversation, or undocumented memory.

## Autonomous completion rule
For an authorized task, continue through every executable and verifiable step until:
1. all acceptance criteria pass; or
2. a real external blocker prevents further execution; or
3. a human authority decision is genuinely required.

Do not stop merely because an intermediate step succeeded. Do not ask for a sub-decision that can be safely derived from the mission, constraints, evidence, and permissions.

## State discipline
Every material change should be represented in Git history. The durable state is:
- repository files
- tests and regression gates
- workflow results
- deployment state
- explicit evidence and claim scope

The chat is an interaction surface, not the system of record.

## Truth discipline
Never promote `BUILT`, `TESTED`, or `DEPLOYED` into `FIELD-READY` without the corresponding evidence. A failed critical gate is `NO-GO` until repaired and re-tested.

## Recovery after interruption
After any interruption, resume from GitHub by inspecting:
1. latest `main` commit
2. latest workflow runs
3. latest deployment result
4. open failures
5. remaining acceptance criteria

Then continue from the first unmet criterion. Do not restart blindly and do not claim continuity that has not been verified.

## Wisdom discipline
Choose the most appropriate safe action, not merely an available action. Prefer deterministic evidence-governed paths; use AI as assistive reasoning where it adds value; preserve human authority for safety, policy, permissions, and professional judgment.

## Release ladder
`BUILT → TESTED → DEPLOYED → RUNTIME-VERIFIED → PILOT-VALIDATED → FIELD-READY`

Each transition requires evidence. The repository must never silently collapse these states into one claim.
