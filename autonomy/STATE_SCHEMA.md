# Autonomous Mission State Contract

Required durable state:

- `mission_id`
- `baseline_id`
- `phase`
- `status`
- `current_task`
- `completed_tasks`
- `open_gaps`
- `blockers`
- `dependencies`
- `attempt_counters`
- `execution_budget`
- `last_checkpoint`
- `artifact_identities`
- `evidence_state`
- `claim_state`
- `release_state`
- `next_best_action`
- `history`

State transitions MUST be explicit and auditable. Checkpoints MUST be written before consequential mutations and validated before resume. Corrupt or contradictory state MUST cause safe stop/recovery rather than silent continuation.
