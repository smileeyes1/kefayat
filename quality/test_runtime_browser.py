#!/usr/bin/env python3
"""Browser-runtime assurance for the shipped static Kefayat Ω artifact.

Scope: real Chromium runtime, desktop/mobile viewports, service-worker control,
offline reload, and offline knowledge access for the locally served release tree.
The report binds evidence to exact artifact hashes. This is strong browser-runtime
evidence, but it is not a physical-device, Gemini-runtime, or school-field claim.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "runtime-browser"
BASE_URL = os.environ.get("KEFAYAT_BASE_URL", "http://127.0.0.1:8765/")
ARTIFACTS = [
    ROOT / "index.html",
    ROOT / "sw.js",
    ROOT / "manifest.webmanifest",
    ROOT / "knowledge" / "competencies.json",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_identity() -> dict:
    items = {}
    combined = hashlib.sha256()
    for path in ARTIFACTS:
        assert path.is_file() and path.stat().st_size > 0, f"missing release artifact: {path}"
        rel = str(path.relative_to(ROOT))
        digest = sha256(path)
        items[rel] = digest
        combined.update(rel.encode("utf-8"))
        combined.update(bytes.fromhex(digest))
    return {"sha256": combined.hexdigest(), "files": items}


def wait_http(url: str, timeout: float = 20.0) -> None:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2) as response:
                if 200 <= response.status < 400:
                    return
        except Exception as exc:  # pragma: no cover - diagnostic path
            last = exc
        time.sleep(0.25)
    raise AssertionError(f"HTTP server did not become ready: {last}")


def assert_shell(page, label: str) -> dict:
    page.wait_for_load_state("networkidle")
    page.locator("h1", has_text="كفايات Ω").wait_for(timeout=15000)
    page.get_by_text("سجل كفاية", exact=False).first.wait_for(timeout=15000)
    result = page.evaluate(
        """() => ({
          title: document.title,
          dir: document.documentElement.dir,
          lang: document.documentElement.lang,
          width: innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          hasWorkspace: !!document.querySelector('#workspace'),
          buttons: document.querySelectorAll('button').length,
          text: document.body.innerText.slice(0, 5000)
        })"""
    )
    assert result["dir"] == "rtl", (label, result)
    assert result["lang"] == "ar", (label, result)
    assert "كفايات Ω" in result["title"], (label, result)
    assert result["hasWorkspace"] and result["buttons"] >= 5, (label, result)
    assert "سجل كفاية" in result["text"], (label, result)
    assert result["scrollWidth"] <= result["width"] + 2, (label, result)
    return result


def run_view(browser, name: str, viewport: dict[str, int]) -> dict:
    errors: list[str] = []
    context = browser.new_context(viewport=viewport, service_workers="allow", locale="ar-PS")
    page = context.new_page()
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(BASE_URL, wait_until="domcontentloaded")
    online = assert_shell(page, f"{name}-online")

    sw = page.evaluate(
        """async () => {
          if (!('serviceWorker' in navigator)) return {supported:false};
          const reg = await navigator.serviceWorker.ready;
          return {supported:true, scope:reg.scope, active:!!reg.active};
        }"""
    )
    assert sw.get("supported") and sw.get("active"), (name, sw)

    # Ensure the page is actively controlled before testing network loss.
    page.reload(wait_until="networkidle")
    controlled = page.evaluate("() => !!navigator.serviceWorker.controller")
    assert controlled, f"service worker did not control {name} page"

    context.set_offline(True)
    page.reload(wait_until="domcontentloaded")
    offline = assert_shell(page, f"{name}-offline")
    offline_probe = page.evaluate(
        """async () => {
          const cacheKeys = await caches.keys();
          const response = await fetch('./knowledge/competencies.json');
          const data = await response.json();
          return {
            cacheKeys,
            fetchOk: response.ok,
            recordCount: Array.isArray(data.records) ? data.records.length : 0,
            coverageCount: Array.isArray(data.coverage) ? data.coverage.length : 0
          };
        }"""
    )
    assert offline_probe["fetchOk"], (name, offline_probe)
    assert offline_probe["recordCount"] > 0, (name, offline_probe)
    assert offline_probe["coverageCount"] > 0, (name, offline_probe)
    assert any(key.startswith("kefayat-shell-") for key in offline_probe["cacheKeys"]), (name, offline_probe)
    assert not errors, (name, errors)

    OUT.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(OUT / f"{name}-offline.png"), full_page=True)
    context.close()
    return {
        "online": online,
        "offline": offline,
        "offline_probe": offline_probe,
        "service_worker": sw,
        "page_errors": errors,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    server = None
    if BASE_URL.startswith("http://127.0.0.1:") or BASE_URL.startswith("http://localhost:"):
        port = BASE_URL.rstrip("/").split(":")[-1]
        server = subprocess.Popen(
            [sys.executable, "-m", "http.server", port, "--bind", "127.0.0.1"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        wait_http(BASE_URL)

    report = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "scope": "REAL_CHROMIUM_LOCAL_RELEASE_TREE",
        "artifact_identity": tree_identity(),
        "not_proven": ["PHYSICAL_DEVICE", "GEMINI_RUNTIME", "SCHOOL_FIELD_PILOT"],
        "base_url": BASE_URL,
        "views": {},
    }
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            report["chromium_version"] = browser.version
            report["views"]["desktop"] = run_view(browser, "desktop", {"width": 1280, "height": 900})
            report["views"]["mobile"] = run_view(browser, "mobile", {"width": 390, "height": 844})
            browser.close()
        report["decision"] = "PASS_BROWSER_RUNTIME_SCOPE"
        (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"decision": report["decision"], "artifact_sha256": report["artifact_identity"]["sha256"], "chromium": report["chromium_version"]}, ensure_ascii=False))
        print("BROWSER RUNTIME ASSURANCE: PASS")
        return 0
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()


if __name__ == "__main__":
    raise SystemExit(main())
