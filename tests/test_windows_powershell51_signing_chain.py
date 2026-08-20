from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORCHESTRATOR = ROOT / "tools" / "windows_russian_production_signing.ps1"
GATE = ROOT / "tools" / "russian_production_release_gate.ps1"
VERIFIER = ROOT / "tools" / "verify_russian_release.ps1"
SIGNER = ROOT / "tools" / "russian_signed_release.ps1"


def test_orchestrator_remains_ascii_only_for_windows_powershell_51():
    raw = ORCHESTRATOR.read_bytes()
    assert all(byte < 128 for byte in raw)


def test_unicode_child_scripts_are_loaded_explicitly_as_utf8():
    text = ORCHESTRATOR.read_text(encoding="ascii")
    assert "function Invoke-Utf8PowerShellScript" in text
    assert "[System.IO.File]::ReadAllText" in text
    assert "[System.Text.Encoding]::UTF8" in text
    assert "[scriptblock]::Create($source)" in text
    assert "russian_signed_release.ps1" in text
    assert "russian_production_release_gate.ps1" in text
    assert "Invoke-Utf8PowerShellScript" in text


def test_bundled_russian_verifier_is_rewritten_with_utf8_bom_before_signing():
    text = ORCHESTRATOR.read_text(encoding="ascii")
    assert "function Convert-FileToUtf8Bom" in text
    assert "0xEF, 0xBB, 0xBF" in text
    assert "verify_russian_release.ps1" in text
    convert_index = text.index("Convert-FileToUtf8Bom -Path")
    signing_index = text.index("=== Physical signing boundary ===")
    assert convert_index < signing_index


def test_downstream_scripts_really_contain_unicode_and_need_the_encoding_boundary():
    assert any(byte >= 128 for byte in GATE.read_bytes())
    assert any(byte >= 128 for byte in VERIFIER.read_bytes())
    assert any(byte >= 128 for byte in SIGNER.read_bytes())
