from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "russian_signed_release.ps1"
DOC = ROOT / "release" / "APL_REL_011_RUSSIAN_SIGNED_RELEASE_INTEGRATION_OTUC_READINESS.md"
WORKFLOW = ROOT / ".github" / "workflows" / "russian-signed-release-readiness.yml"


def test_rel011_files_exist():
    assert SCRIPT.is_file()
    assert DOC.is_file()
    assert WORKFLOW.is_file()


def test_script_never_accepts_pin_or_pfx():
    text = SCRIPT.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "[string]$pin" not in lowered
    assert "password" not in lowered
    assert "pfx" not in lowered
    assert "p12" not in lowered
    assert "private_key_export_attempted      = $false" in lowered
    assert "pin_stored                        = $false" in lowered


def test_script_requires_exact_release_identity():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "[string]$Version" in text
    assert "[string]$GitTag" in text
    assert "[string]$GitCommit" in text
    assert "^[0-9a-fA-F]{40}$" in text
    assert "Version/tag mismatch" in text


def test_script_covers_final_assets_with_sha256_and_detached_signature():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "SHA256SUMS.txt" in text
    assert "SHA256SUMS.txt.sig" in text
    assert "Get-FileHash" in text
    assert "-Algorithm SHA256" in text
    assert "'-sfsign', '-sign', '-detached', '-add'" in text
    assert "'-sfsign', '-verify', '-detached'" in text
    assert "Release asset changed during signing" in text


def test_script_exports_public_certificate_and_non_secret_evidence():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "Export-Certificate" in text
    assert "signer-certificate.cer" in text
    assert "signing-evidence.json" in text
    assert "signer_subject" in text
    assert "signer_thumbprint" in text
    assert "git_commit" in text
    assert "assets" in text


def test_embedded_signing_remains_disabled_until_separate_otuc_poc():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "$embeddedCodeSigningActivated = $false" in text
    assert "otuc_production_certificate_used  = $false" in text
    assert "RELEASE-EVIDENCE-ONLY" in text
    assert "CODE-SIGNING-CANDIDATE-ONLY" in text


def test_doc_records_current_rel010_certificate_classification_and_otuc_gate():
    text = DOC.read_text(encoding="utf-8")
    assert "RELEASE-EVIDENCE-ONLY" in text
    assert "EE1CFA955BA22F03C39C76B183D94CD37494582E" in text
    assert "ОТУЦ" in text
    assert "test" in text.lower() or "тест" in text.lower()
    assert "production" in text.lower()


def test_readiness_workflow_is_non_secret_and_does_not_sign():
    text = WORKFLOW.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "permissions:" in text
    assert "contents: read" in text
    assert "pytest" in lowered
    assert "rutoken" not in lowered
    assert "csptest" not in lowered
    assert "certificate" not in lowered
    assert "secrets." not in lowered
