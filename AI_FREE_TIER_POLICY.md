# KEFAYAT — Real AI / Free-Tier Policy

## Purpose
Kefayat includes a real Gemini AI integration while keeping the project owner's infrastructure cost at zero for inference by default.

## Architecture
- Deterministic knowledge base remains authoritative.
- AI is an assistive generation layer.
- The default AI model is `gemini-2.5-flash-lite`.
- The user supplies their own Gemini API key through the app.
- The key is stored locally in the browser/WebView and is sent directly to Google's Gemini API.
- No shared project API key is embedded in the public repository.
- No server-side proxy is required for the free user-owned path.

## Free means quota-limited
Google's Gemini API currently offers free-tier access for selected models, but it is quota/rate limited and the limits can change. Free tier must never be represented as unlimited or guaranteed forever.

## Cost controls
1. Local knowledge retrieval before AI.
2. Cache-first behavior where implemented.
3. Small default model and bounded output.
4. No automatic paid fallback.
5. On quota/provider failure, keep the application usable locally.
6. Never silently switch a user to paid billing.

## Security
- Never commit API keys.
- Never put an owner-wide secret in client assets.
- Never collect Google passwords.
- Use Google's supported API authorization/key mechanisms.

## Anti-circumvention
Kefayat must not evade quotas, rotate identities to bypass limits, spoof usage, or otherwise circumvent provider controls.

## Assurance
A successful Gemini response is not curriculum proof. Generated educational material must remain subject to the deterministic knowledge layer and MASTER Ω assurance gates.
