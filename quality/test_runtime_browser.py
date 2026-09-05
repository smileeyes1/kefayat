#!/usr/bin/env python3
"""Browser-runtime assurance for the shipped static Kefayat Ω artifact.

Scope: real Chromium runtime, desktop/mobile viewports, service-worker control,
offline reload/knowledge access, Intent Contract execution, and real PDF artifact
creation for the canonical math fixture. Evidence is bound to exact release-tree
hashes. This is not a physical-device, Gemini-runtime, or school-field claim.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import struct
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
    ROOT / "intent" / "intent-engine.js",
    ROOT / "artifact" / "pdf-artifact-engine.js",
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
          hasIntent: typeof KefayatIntent === 'object',
          hasArtifact: typeof KefayatArtifact === 'object',
          text: document.body.innerText.slice(0, 7000)
        })"""
    )
    assert result["dir"] == "rtl", (label, result)
    assert result["lang"] == "ar", (label, result)
    assert "كفايات Ω" in result["title"], (label, result)
    assert result["hasWorkspace"] and result["buttons"] >= 5, (label, result)
    assert result["hasIntent"] and result["hasArtifact"], (label, result)
    assert "سجل كفاية" in result["text"], (label, result)
    assert result["scrollWidth"] <= result["width"] + 2, (label, result)
    return result


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"not PNG: {path}"
    return struct.unpack(">II", data[16:24])


def validate_rendered_pdf(path: Path, label: str) -> dict:
    data = path.read_bytes()
    assert len(data) > 20_000, (label, len(data))
    assert data.startswith(b"%PDF-1.4\n"), label
    assert data.rstrip().endswith(b"%%EOF"), label
    assert b"/Type /Pages /Count 2" in data, label
    sx = re.search(rb"startxref\n(\d+)\n%%EOF", data)
    assert sx and data[int(sx.group(1)):int(sx.group(1))+4] == b"xref", label

    pdfinfo = subprocess.run(["pdfinfo", str(path)], text=True, capture_output=True, check=False)
    assert pdfinfo.returncode == 0, (label, pdfinfo.stderr)
    pages = re.search(r"^Pages:\s+(\d+)", pdfinfo.stdout, re.MULTILINE)
    assert pages and int(pages.group(1)) == 2, (label, pdfinfo.stdout)
    assert re.search(r"^Page size:\s+595(?:\.\d+)? x 842(?:\.\d+)? pts", pdfinfo.stdout, re.MULTILINE), (label, pdfinfo.stdout)

    prefix = OUT / f"{label}-render"
    rendered = subprocess.run(["pdftoppm", "-png", "-r", "100", str(path), str(prefix)], text=True, capture_output=True, check=False)
    assert rendered.returncode == 0, (label, rendered.stderr)
    pngs = sorted(OUT.glob(f"{label}-render-*.png"))
    assert len(pngs) == 2, (label, pngs)
    page_evidence = []
    for p in pngs:
        w, h = png_size(p)
        assert w >= 800 and h >= 1100 and p.stat().st_size > 20_000, (p, w, h, p.stat().st_size)
        page_evidence.append({"file": p.name, "width": w, "height": h, "sha256": sha256(p), "bytes": p.stat().st_size})
    return {"file": path.name, "sha256": sha256(path), "bytes": len(data), "pdfinfo": pdfinfo.stdout, "rendered_pages": page_evidence}


def exercise_canonical_intent(page, label: str) -> dict:
    page.locator("#goal").fill("أنشئ درس الجمع ضمن ١٠ كملف PDF")
    with page.expect_download(timeout=30000) as download_info:
        page.locator("#drive").click()
    download = download_info.value
    target = OUT / f"{label}-canonical-intent.pdf"
    download.save_as(str(target))

    page.locator("#artifact a.download-link").wait_for(timeout=15000)
    contract_text = page.locator("#contract").inner_text()
    result_text = page.locator("#result").inner_text()
    assert "READY FOR EXECUTION" in contract_text, (label, contract_text)
    assert "الرياضيات" in contract_text, (label, contract_text)
    assert "الصف: ١" in contract_text, (label, contract_text)
    assert "PALESTINIAN_EDUCATION" in contract_text, (label, contract_text)
    assert "P0_GOLDEN_RENDER" in contract_text, (label, contract_text)
    assert "pdf" in contract_text.lower(), (label, contract_text)
    assert "Acceptance Oracle:" in result_text, (label, result_text)
    assert page.locator("#artifact img.artifact-preview").count() == 2, label

    runtime = page.evaluate(
        """() => ({
          contract: S.last.contract,
          gate: S.last.gate,
          evidence: S.last.artifact && S.last.artifact.evidence,
          filename: S.last.artifact && S.last.artifact.filename,
          bytes: S.last.artifact && S.last.artifact.bytes.length
        })"""
    )
    assert runtime["gate"]["pass"] is True, runtime
    assert runtime["contract"]["subject"] == "mathematics", runtime
    assert runtime["contract"]["grade"] == 1, runtime
    assert runtime["contract"]["artifact_type"] == "pdf", runtime
    ev = runtime["evidence"]
    assert ev["actual_pdf_exists"] is True, ev
    assert ev["student_eye_math_pass"] is True, ev
    assert ev["eastern_digits_pass"] is True, ev
    assert ev["equals_position_pass"] is True, ev
    assert ev["page_count"] == 2, ev
    assert ev["student_eye_strings"] == ["٤ + ٣ = □", "٥ + ٢ = □", "١ + ٨ = □", "٦ + ٣ = □"], ev
    assert ev["engine_requests"] == ["□ = ٣ + ٤", "□ = ٢ + ٥", "□ = ٨ + ١", "□ = ٣ + ٦"], ev
    external = validate_rendered_pdf(target, label)
    return {"contract": runtime["contract"], "generator_evidence": ev, "external_pdf_validation": external}


def run_view(browser, name: str, viewport: dict[str, int]) -> dict:
    errors: list[str] = []
    context = browser.new_context(viewport=viewport, service_workers="allow", locale="ar-PS", accept_downloads=True)
    page = context.new_page()
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(BASE_URL, wait_until="domcontentloaded")
    online = assert_shell(page, f"{name}-online")
    online_intent = exercise_canonical_intent(page, f"{name}-online")

    sw = page.evaluate(
        """async () => {
          if (!('serviceWorker' in navigator)) return {supported:false};
          const reg = await navigator.serviceWorker.ready;
          return {supported:true, scope:reg.scope, active:!!reg.active};
        }"""
    )
    assert sw.get("supported") and sw.get("active"), (name, sw)

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
    offline_intent = exercise_canonical_intent(page, f"{name}-offline")
    assert not errors, (name, errors)

    OUT.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(OUT / f"{name}-offline.png"), full_page=True)
    context.close()
    return {
        "online": online,
        "online_intent": online_intent,
        "offline": offline,
        "offline_probe": offline_probe,
        "offline_intent": offline_intent,
        "service_worker": sw,
        "page_errors": errors,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*"):
        if old.is_file():
            old.unlink()
    assert subprocess.run(["pdfinfo", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False).returncode == 0, "poppler pdfinfo required"
    assert subprocess.run(["pdftoppm", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False).returncode == 0, "poppler pdftoppm required"

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
        "scope": "REAL_CHROMIUM_INTENT_AND_PDF_LOCAL_RELEASE_TREE",
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
        report["decision"] = "PASS_BROWSER_INTENT_PDF_RUNTIME_SCOPE"
        (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"decision": report["decision"], "artifact_sha256": report["artifact_identity"]["sha256"], "chromium": report["chromium_version"]}, ensure_ascii=False))
        print("BROWSER INTENT + PDF RUNTIME ASSURANCE: PASS")
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
