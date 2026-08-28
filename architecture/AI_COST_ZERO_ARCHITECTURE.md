# KEFAYAT — AI Cost-Minimization Architecture

## Objective
Maximize useful AI capability while making cloud AI optional and keeping application operation at zero cloud-AI calls whenever the task can be completed locally.

## Non-negotiable boundary
Zero cost means zero application-controlled paid API dependency by default. It does NOT mean bypassing provider quotas, authentication, rate limits, terms, or platform restrictions.

## Execution priority
1. Deterministic local rules.
2. Local curriculum knowledge base.
3. Local search/index.
4. Local cache and exact-result reuse.
5. Local model when available and appropriate.
6. Authorized free-tier cloud model only when necessary.
7. Safe local fallback when cloud capacity is unavailable.

## AI Gate
A cloud request is permitted only when:
- the task genuinely needs generative/model capability;
- deterministic/local processing cannot satisfy the requirement adequately;
- an equivalent cached result is unavailable;
- the request is within the configured budget and provider limits;
- privacy and authorization requirements permit transmission;
- use complies with the provider's current terms.

## Cache key
A reproducible request fingerprint should include, as applicable:
- task type;
- grade;
- subject;
- competency ID;
- normalized constraints;
- knowledge-base version;
- prompt/template version;
- model capability class.

Equivalent requests MUST reuse cached results when safe.

## Quota governor
The runtime maintains a local quota state:
- NORMAL: local-first, cloud allowed only after AI Gate.
- LOW: aggressively prefer cache/local model; cloud restricted.
- EXHAUSTED: cloud disabled; local-only mode.
- UNKNOWN: fail closed for nonessential cloud calls.

## Provider abstraction
The application must not hard-code one cloud provider into core business logic. Use an adapter boundary so authorized providers or local inference can be changed without changing curriculum logic.

## Privacy
Curriculum and deterministic validation should remain local. Sensitive user content must not be transmitted merely because an AI endpoint exists.

## Offline requirement
Core competency browsing, mapping, validation, lesson templates, assessment rules, evidence ledger, and saved mission state should remain usable without cloud AI.

## Observability
Record locally:
- cloud_call_count;
- cache_hit_count;
- local_resolution_count;
- cloud_block_reason;
- estimated token/request usage when available;
- quota state;
- model/provider class;
- timestamp;
- knowledge version.

Do not store secrets in repository files, browser source, or logs.

## Acceptance criteria
- Core deterministic workflows require zero cloud-AI calls.
- Repeated equivalent requests are served from cache when valid.
- Cloud AI can be disabled without breaking core application workflows.
- Quota exhaustion automatically switches to local-only operation.
- No mechanism bypasses quotas, authentication, billing, rate limits, or provider terms.
- AI output remains untrusted until MASTER Ω validation passes.
