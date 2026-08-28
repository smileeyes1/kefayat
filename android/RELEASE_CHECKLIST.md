# KEFAYAT Android — Release Gate

## Already implemented
- Android application shell.
- Offline-first packaged web application path.
- Generated competency knowledge is staged into APK assets during CI.
- Automated debug APK build.
- APK existence and non-empty checks.
- Bundled knowledge-base existence check.
- Production release workflow for signed APK + AAB.
- APK signature verification with `apksigner`.
- Signing material cleanup after CI.

## Required before production publication
1. Configure GitHub Actions secrets:
   - `KEFAYAT_KEYSTORE_B64`
   - `KEFAYAT_STORE_PASSWORD`
   - `KEFAYAT_KEY_ALIAS`
   - `KEFAYAT_KEY_PASSWORD`
2. Enable/configure GitHub Pages if the web deployment is required.
3. Run the signed release workflow.
4. Inspect the generated APK/AAB and verify application identity.
5. Perform a real-device pilot covering offline launch, competency search, lesson workflow, assessment workflow, persistence, and recovery.
6. Review curriculum provenance and Islamic authenticity evidence before any claim of official status.
7. For Google Play, complete Play Console registration, store listing, policy declarations, testing track, and Play App Signing configuration.

## No false release claim
The repository is not considered production-proven merely because the build pipeline exists. A production release requires successful build evidence, install/runtime evidence, real-device verification, and the applicable release/account configuration.
