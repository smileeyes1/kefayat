# KEFAYAT Ω — LOCAL-FIRST / ZERO-COST-BY-DEFAULT ARCHITECTURE

## Objective
Minimize cloud AI/API consumption and make ordinary application operation independent of paid services, while never bypassing provider limits or terms.

## Operating principle
`LOCAL → CACHE → LOCAL MODEL → ALLOWED FREE PROVIDER → SAFE PAUSE/RESUME`

Cloud AI is an accelerator, not the curriculum source of truth and not a required dependency for deterministic functions.

## Zero-API path
The following must execute locally whenever possible:
- competency lookup and filtering
- provenance and schema validation
- deterministic mapping
- coverage calculations
- search over bundled knowledge
- state management
- caching and request fingerprinting
- deterministic assessment logic
- mathematical order validation
- graphics count validation when an inspectable artifact is locally available
- evidence/traceability bookkeeping

## Cloud-AI gate
A cloud request is permitted only when all applicable checks pass:
1. The task genuinely requires generative/model capability.
2. Local deterministic logic cannot safely complete it.
3. Cache lookup was performed.
4. Duplicate requests were collapsed.
5. The smallest sufficient context is selected.
6. Provider quota/terms allow the request.
7. No secret or sensitive data is sent unnecessarily.

## Cache key
Use a stable fingerprint over the semantic inputs, knowledge version, policy version, and prompt/model version. Identical requests must reuse cached results rather than consume another cloud request.

## Quota governor
Track usage per provider and user-owned credential where applicable. Enter `LOCAL_ONLY` before the provider limit is reached. Do not create or rotate accounts, credentials, IPs, or parallel requests to evade limits.

## Continuity
Persist queue, checkpoints, cached outputs, evidence, and blockers. If a provider becomes unavailable or a quota becomes unavailable, preserve work and resume later or continue through an allowed fallback.

## Offline posture
The core educational experience should remain usable after the initial application/knowledge assets are cached. A service worker may cache the application shell; authoritative knowledge updates remain versioned and provenance-controlled.

## User experience
Expose a simple status surface. Hide implementation complexity, but never hide material facts about permissions, privacy, quota state, or blocked actions.

## Cost claim
The architecture targets `ZERO-COST-BY-DEFAULT` and `ZERO-CLOUD-CALLS-FOR-DETERMINISTIC-WORK`. It does not claim unlimited free provider capacity or zero resource consumption.

## Acceptance criteria
- App loads without a cloud AI dependency.
- Deterministic competency browsing works without an API.
- Repeated identical AI requests can be served from cache.
- Cloud calls are blocked when policy denies them.
- Quota exhaustion does not destroy persisted mission state.
- Provider limits are never bypassed.
- Secrets are not committed to the repository.
- Offline shell can recover after network loss.
