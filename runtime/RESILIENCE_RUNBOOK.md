# KEFAYAT Resilience Runbook

## Target
Keep the application useful when cloud AI, a provider quota, a deployment, or a single execution route is unavailable.

## Route order
1. Deterministic rules and validators.
2. Persistent local cache.
3. Local model.
4. Authorized free/available cloud provider.
5. Safe blocked state with checkpoint and resumable queue.

## Provider failure
Detect timeout, authentication failure, quota exhaustion, rate limiting, malformed response, and policy rejection separately. Do not retry indefinitely. Retry only transient failures with bounded exponential backoff. Quota/authentication failures switch route instead of consuming retries.

## Persistence
Mission state, evidence state, queue position, route decision, and artifact identity must be checkpointed before a consequential transition and after a successful transition.

## Multi-host continuity
The application must be deployable as a static/PWA client plus optional lightweight control service. A self-hosted runner may provide durable scheduled execution when a continuously available user-controlled machine exists. GitHub-hosted Actions can remain the CI safety net. These are complementary, not interchangeable.

## Zero-cost posture
Static assets, deterministic processing, local storage, local computation, and cached knowledge should handle the normal path. Cloud inference is an exception. No mechanism is allowed to evade quotas or provider restrictions.

## Degraded modes
OFFLINE: local knowledge + deterministic rules + cached results.
LOCAL_ONLY: cloud disabled, local model permitted.
CACHE_ONLY: return known valid results; queue new work.
RECOVERY: process queued work when a route becomes available.

## Safety
Never expose API keys in the client bundle or repository. Never use a user's provider password. Never treat a free allocation as unlimited. Never claim continuous execution unless an actual continuously running host/service exists.
