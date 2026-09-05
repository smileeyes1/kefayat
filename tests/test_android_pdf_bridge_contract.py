#!/usr/bin/env python3
"""Static security/packaging contract for Android PDF fulfillment bridge."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
JAVA=ROOT/'android/app/src/main/java/com/kefayat/gem/MainActivity.java'
ADAPTER=ROOT/'artifact/android-webview-bridge.js'
BUILD=ROOT/'android/build.gradle'
APP=ROOT/'android/app/build.gradle'
PRODUCTION=ROOT/'.github/workflows/production-gate.yml'
SIGNED=ROOT/'.github/workflows/android-release.yml'


def main()->None:
    for p in (JAVA,ADAPTER,BUILD,APP,PRODUCTION,SIGNED):
        assert p.is_file() and p.stat().st_size>0,p
    java=JAVA.read_text(encoding='utf-8')
    for marker in ('addJavascriptInterface(new PdfBridge(), "KefayatAndroid")','beginPdf','appendPdfChunk','finishPdf','MediaStore.Downloads','RELATIVE_PATH','MIXED_CONTENT_NEVER_ALLOW','LOCAL_PREFIX','android-webview-bridge.js'):
        assert marker in java,marker
    assert 'setAllowContentAccess(false)' in java
    adapter=ADAPTER.read_text(encoding='utf-8')
    for marker in ('CHUNK_BYTES=48*1024','KefayatAndroid.beginPdf','KefayatAndroid.appendPdfChunk','KefayatAndroid.finishPdf','KefayatArtifact.downloadArtifact','KEFAYAT_ANDROID_PDF_BRIDGE_FALLBACK'):
        assert marker in adapter,marker
    build=BUILD.read_text(encoding='utf-8')
    assert "version '8.10.0'" in build,build
    app=APP.read_text(encoding='utf-8')
    assert 'compileSdk 36' in app and 'targetSdk 36' in app
    for workflow in (PRODUCTION.read_text(encoding='utf-8'),SIGNED.read_text(encoding='utf-8')):
        assert "gradle-version: '8.11.1'" in workflow
        assert 'assets/artifact/android-webview-bridge.js' in workflow
        assert 'artifact/android-webview-bridge.js' in workflow
    print('ANDROID PDF BRIDGE CONTRACT: PASS')

if __name__=='__main__':main()
