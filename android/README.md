# KEFAYAT Android Release Track

This directory defines the release target for the Android application.

## Release gates
- Build reproducibly with Gradle.
- Debug build must install and launch.
- Release build must be signed with a private release/upload key stored outside source control.
- Core workflows must work without cloud AI.
- Offline/local-only mode must remain functional.
- Knowledge-base integrity and version must be checked at startup.
- MASTER Ω assurance tests must pass before release.
- APK identity/hash must be recorded as release evidence.

## Distribution
For direct APK distribution, publish a signed release APK.
For Google Play, prefer an Android App Bundle (AAB) and Play App Signing; keep the upload key separate and secret.

## Security
Never commit keystores, passwords, API keys, OAuth client secrets, or provider credentials.
