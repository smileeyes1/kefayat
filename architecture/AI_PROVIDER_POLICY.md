# KEFAYAT — AI Provider Policy

## Provider-neutral design
Core curriculum, assurance, and application logic must not depend on a specific AI vendor.

## Allowed provider classes
- LOCAL_MODEL
- AUTHORIZED_FREE_TIER
- USER_AUTHORIZED_PROVIDER

## Disallowed behavior
The application must never:
- bypass quotas or rate limits;
- rotate identities to evade limits;
- scrape private endpoints;
- embed shared secrets in client code;
- collect user passwords for provider accounts;
- misrepresent usage or identity;
- treat a free tier as unlimited.

## Selection
Provider selection is capability- and policy-based. Prefer the least-cost/least-data route that satisfies the requirement.

## User-owned credentials
If a provider requires an API key, OAuth token, or account authorization, the application must use the provider's supported authorization mechanism. Credentials belong to the user or deployment owner and must not be committed to GitHub.

## Failure behavior
When a provider is unavailable, rate-limited, or exhausted, the system automatically falls back to cache/local deterministic processing/local model where possible. Core workflows must not fail solely because cloud AI is unavailable.
