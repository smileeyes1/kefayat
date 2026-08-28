from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AI = ROOT / "ai.html"


def test_ai_workspace_exists():
    assert AI.is_file()


def test_ai_workspace_uses_free_tier_model():
    text = AI.read_text(encoding="utf-8")
    assert "gemini-2.5-flash-lite" in text
    assert "generativelanguage.googleapis.com" in text


def test_ai_workspace_does_not_embed_a_project_secret():
    text = AI.read_text(encoding="utf-8")
    assert "AIza" not in text
    assert "KEFAYAT_API_KEY" not in text


def test_ai_workspace_keeps_key_local():
    text = AI.read_text(encoding="utf-8")
    assert "localStorage" in text
    assert "kefayat.gemini.apiKey" in text


def test_android_release_packages_ai():
    workflow = (ROOT / ".github/workflows/android-release.yml").read_text(encoding="utf-8")
    assert "cp index.html ai.html" in workflow
