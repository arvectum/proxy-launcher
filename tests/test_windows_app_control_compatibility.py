from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSESS = ROOT / "tools" / "windows_app_control_assess.ps1"
PACK = ROOT / "tools" / "windows_app_control_enterprise_trust_pack.ps1"
OWNER = ROOT / "tools" / "windows_owner_source_mode.ps1"
DOC = ROOT / "docs" / "WINDOWS_APP_CONTROL_COMPATIBILITY.md"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_powershell_scripts_are_ascii_safe_for_windows_powershell_51():
    for path in (ASSESS, PACK, OWNER):
        assert all(byte < 128 for byte in path.read_bytes()), path


def test_assessment_is_read_only_and_does_not_change_app_control_state():
    body = text(ASSESS)
    assert "VerifiedAndReputablePolicyState" in body
    assert "CiTool.exe" in body
    assert "Get-AuthenticodeSignature" in body
    for forbidden in (
        "Set-ItemProperty",
        "Remove-ItemProperty",
        "--update-policy",
        "--remove-policy",
        "Set-CIPolicy",
    ):
        assert forbidden not in body


def test_enterprise_pack_verifies_exact_russian_release_before_policy_generation():
    body = text(PACK)
    verifier = body.index("Invoke-ReleaseVerifier -Verifier $verifier -Directory $ReleaseDirectory")
    policy = body.index("New-CIPolicy -MultiplePolicyFormat")
    assert verifier < policy
    assert "5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414" in body
    assert "62d313547b4d8c2c8e6951d6cd866bb954fdf199ad7650063c8ed3bfbc455801" in body
    assert "f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a" in body
    assert "EE1CFA955BA22F03C39C76B183D94CD37494582E" in body


def test_enterprise_pack_generates_supplemental_exact_hash_policy_only():
    body = text(PACK)
    assert "[Guid]$BasePolicyId" in body
    assert "-Level Hash" in body
    assert "-MultiplePolicyFormat" in body
    assert "-SupplementsBasePolicyID $BasePolicyId" in body
    assert "ConvertFrom-CIPolicy" in body
    assert "ReferenceFullHash" in body
    assert "BootstrapHash" in body


def test_enterprise_pack_never_deploys_or_weakens_windows_protection():
    body = text(PACK)
    assert "never deploys App Control policy" in body
    assert "Smart App Control must not be disabled" in body
    for forbidden in (
        "CiTool --update-policy",
        "CiTool.exe --update-policy",
        "VerifiedAndReputablePolicyState",
        "Set-ItemProperty",
        "reg.exe add",
    ):
        assert forbidden not in body


def test_reference_full_hash_requires_exact_sealed_reference_installation():
    body = text(PACK)
    assert "Reference installation does not contain the exact sealed application EXE." in body
    assert "Reference cached repair Setup does not match the exact production installer." in body
    assert "installed-reference-tree" in body


def test_owner_source_mode_is_explicitly_nonproduction_and_never_changes_app_control():
    body = text(OWNER)
    assert "production_distribution = $false" in body
    assert "Smart App Control is not disabled" in body
    assert "App Control policy is not changed" in body
    assert "source mode is owner/developer profile only" in body
    for forbidden in (
        "VerifiedAndReputablePolicyState",
        "CiTool",
        "Set-CIPolicy",
        "ConvertFrom-CIPolicy",
    ):
        assert forbidden not in body


def test_documentation_keeps_russian_provenance_separate_from_windows_execution_trust():
    body = text(DOC)
    assert "Russian" in body
    assert "Smart App Control" in body
    assert "App Control for Business" in body
    assert "Managed Installer" in body
    assert "hash" in body.lower()
    assert "do not" in body.lower()
