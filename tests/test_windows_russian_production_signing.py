from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "windows_russian_production_signing.ps1"
DOC = ROOT / "docs" / "WINDOWS_RUSSIAN_FIRST_PRODUCTION_SIGNING.md"
WORKFLOW = ROOT / ".github" / "workflows" / "windows-russian-production-signing.yml"
EVIDENCE = ROOT / "docs" / "evidence" / "WINDOWS_INNO_6_7_1_PRODUCTION_BUILD_EVIDENCE.json"


def _script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_windows_signing_contract_files_exist():
    assert SCRIPT.is_file()
    assert DOC.is_file()
    assert WORKFLOW.is_file()
    assert EVIDENCE.is_file()


def test_ceremony_is_owner_operated_windows_only_and_requires_main_clean_tagged_head():
    text = _script()
    assert "$env:OS -ne 'Windows_NT'" in text
    assert "Signing ceremony requires canonical branch main" in text
    assert "Git worktree must be clean before production signing" in text
    assert "Release tag must resolve to current canonical HEAD before signing" in text


def test_ceremony_never_accepts_pin_password_pfx_or_exportable_key_material():
    lowered = _script().lower()
    assert "[string]$pin" not in lowered
    assert "[string]$password" not in lowered
    assert "[string]$pfx" not in lowered
    assert "import-pfxcertificate" not in lowered
    assert "export-pfxcertificate" not in lowered
    assert "private key" in lowered
    assert "pin is never passed to this script" in lowered


def test_exact_023_portable_and_installer_are_bound_to_build_evidence():
    text = _script()
    assert "WINDOWS_INNO_6_7_1_PRODUCTION_BUILD_EVIDENCE.json" in text
    assert "portable_build.zip_sha256" in text
    assert "installer_build.sha256" in text
    assert "installer_build.bytes" in text
    assert "Portable ZIP is not the sealed production artifact" in text
    assert "Installer is not the sealed production artifact" in text


def test_artifact_build_commit_and_release_policy_commit_are_distinct_provenance_fields():
    text = _script()
    assert "artifact_build_commit" in text
    assert "release_policy_commit" in text
    assert "sealed-build-artifacts-with-release-only-delta" in text
    assert "Assert-ReleaseOnlyDelta" in text
    assert "Product/build-input drift exists after the sealed artifact build" in text


def test_release_only_delta_does_not_allow_runtime_product_files():
    text = _script()
    assert "'^docs/'" in text
    assert "'^release/'" in text
    assert "'^tests/'" in text
    assert "'^\\.github/'" in text
    assert "^tools/windows_russian_production_signing\\.ps1$" in text
    assert "^proxy_" not in text
    assert "^windows_backend" not in text
    assert "^ArvectumProxyLauncherSetup" not in text


def test_release_directory_must_be_outside_repo_and_empty():
    text = _script()
    assert "ReleaseDirectory must be outside the Git worktree" in text
    assert "ReleaseDirectory already exists and is not empty" in text


def test_customer_release_set_contains_provenance_notices_license_and_verifier():
    text = _script()
    assert "WINDOWS_BUILD_PROVENANCE.json" in text
    assert "THIRD_PARTY_NOTICES.txt" in text
    assert "LICENSE.txt" in text
    assert "README_RUSSIAN_RELEASE.txt" in text
    assert "prepare_russian_release_verification_ux.ps1" in text


def test_ceremony_reuses_governed_rel011_and_rel013_fail_closed_primitives():
    text = _script()
    assert "russian_signed_release.ps1" in text
    assert "russian_production_release_gate.ps1" in text
    assert "ExpectedSignerThumbprint" in text
    assert "Production gate did not issue PUBLISH" in text


def test_authenticode_and_smartscreen_are_explicitly_not_claimed():
    text = _script()
    assert "embedded_pe_authenticode = $false" in text
    assert "microsoft_smartscreen_trust_claimed = $false" in text
    assert "RELEASE-EVIDENCE-ONLY" in text
    assert "Embedded Authenticode/SmartScreen trust claimed: NO" in text


def test_workflow_is_non_secret_contract_and_windows_parse_only():
    text = WORKFLOW.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "contents: read" in lowered
    assert "pytest" in lowered
    assert "windows-latest" in lowered
    assert "parser]::parseinput" in lowered
    assert "${{ secrets." not in lowered
    assert "rutoken" not in lowered
    assert "csptest" not in lowered
