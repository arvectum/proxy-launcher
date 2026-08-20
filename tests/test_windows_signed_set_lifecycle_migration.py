from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "windows_signed_set_lifecycle_acceptance_migration.ps1"


def body() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_script_is_ascii_safe_for_windows_powershell_51():
    assert all(byte < 128 for byte in SCRIPT.read_bytes())


def test_owner_host_execution_is_fail_closed_by_default():
    text = body()
    gate = text.index("if (-not $IsolatedAcceptanceEnvironment)")
    block = text.index("APL-REL-014 OWNER-HOST SAFETY BLOCK", gate)
    delegate = text.index("$baseScript = Join-Path", block)
    assert gate < block < delegate


def test_isolated_environment_switch_is_explicit():
    text = body()
    assert "[switch]$IsolatedAcceptanceEnvironment" in text
    assert "disposable/isolated Windows VM" in text
    assert "dedicated clean acceptance host" in text


def test_incident_reference_and_security_boundary_are_present():
    text = body()
    assert "2026-08-20" in text
    assert "Smart App Control" in text
    assert "Do not disable Smart App Control" in text
    assert "APL_REL_014_OWNER_HOST_INCIDENT_2026-08-20.md" in text


def test_historical_owner_host_mutation_logic_is_removed():
    text = body()
    for forbidden in (
        "Stop-LegacyProcesses",
        "Start-LegacyRuntime",
        "Move-Item -LiteralPath $installRoot",
        "Remove-Item -LiteralPath $UserUninstallKey",
        "Get-LegacyProcesses",
        "rescueRoot",
        "legacyExeSha256",
    ):
        assert forbidden not in text


def test_isolated_gate_delegates_only_to_canonical_acceptance():
    text = body()
    assert "windows_signed_set_lifecycle_acceptance.ps1" in text
    assert "Delegating to canonical exact signed-set lifecycle acceptance." in text
    assert "Start-Process" in text
    assert "Canonical isolated APL-REL-014 acceptance failed" in text
    assert "APL-REL-014 isolated-environment acceptance: PASS" in text
