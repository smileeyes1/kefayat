#!/usr/bin/env python3
"""Fail fast if the shipped inline application JavaScript is syntactically invalid."""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, flags=re.IGNORECASE | re.DOTALL)
    assert scripts, "index.html has no inline application script"
    node = shutil.which("node")
    assert node, "Node.js is required for JavaScript syntax qualification"
    with tempfile.TemporaryDirectory(prefix="kefayat-js-syntax-") as tmp:
        for idx, source in enumerate(scripts, start=1):
            path = Path(tmp) / f"inline-{idx}.js"
            path.write_text(source, encoding="utf-8")
            proc = subprocess.run([node, "--check", str(path)], text=True, capture_output=True, check=False)
            assert proc.returncode == 0, f"JavaScript syntax failure in inline script {idx}:\n{proc.stderr}"
    print(f"INDEX JAVASCRIPT SYNTAX: PASS ({len(scripts)} inline script(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
