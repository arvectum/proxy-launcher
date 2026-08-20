from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "windows_signed_set_lifecycle_acceptance_drift.ps1"


def text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_drift_wrapper_exists_and_is_windows_powershell_51_safe_ascii():
    assert SCRIPT.is_file()
    assert all(byte < 128 for byte in SCRIPT.read_bytes())


def test_exact_installed_identity_is_validated_before_repair_cache_staging():
    value = text()
    exe_check = "if ((Get-Sha256 $exe) -ne $ExpectedApplicationSha256)"
    owner_check = "if ($markerValue -cne $ExpectedOwnerMarker)"
    stage = "Copy-Item -LiteralPath $setup -Destination $temporaryRepair -Force"
    assert exe_check in value
    assert owner_check in value
    assert stage in value
    assert value.index(exe_check) < value.index(stage)
    assert value.index(owner_check) < value.index(stage)


def test_signed_release_is_verified_before_any_repair_cache_staging():
    value = text()
    verify = "Invoke-ReleaseVerifier"
    stage = "Copy-Item -LiteralPath $setup -Destination $temporaryRepair -Force"
    assert "Signed release installer hash mismatch before drift handling." in value
    assert verify in value
    assert stage in value
    assert value.index("Write-Host '=== Drift preflight: exact signed release verification ==='") < value.index(stage)
    assert value.index("Invoke-ReleaseVerifier", value.index("=== Drift preflight")) < value.index(stage)


def test_present_wrong_repair_cache_fails_closed():
    value = text()
    assert "Existing repair cache is present but does not match the exact signed production installer." in value
    assert "-not $repairWasMissing -and (Get-Sha256 $repair) -ne $ExpectedSetupSha256" in value


def test_missing_repair_cache_is_staged_with_exact_hash_then_delegated():
    value = text()
    assert "$repairWasMissing = -not (Test-Path -LiteralPath $repair -PathType Leaf)" in value
    assert "Temporary repair-cache staging hash mismatch." in value
    assert "Staged repair cache does not match the exact signed installer." in value
    assert "windows_signed_set_lifecycle_acceptance_runtime.ps1" in value
    assert "Invoke-RuntimeAcceptance" in value


def test_staged_repair_cache_is_removed_in_finally_to_restore_original_state():
    value = text()
    assert "finally {" in value
    assert "if ($repairWasMissing -and (Test-Path -LiteralPath $repair -PathType Leaf))" in value
    assert "Remove-Item -LiteralPath $repair -Force" in value
    assert "repair_cache_original_state_restored" in value
    assert "Repair-cache drift restoration BLOCK" in value


def test_evidence_distinguishes_preexisting_drift_from_release_lifecycle_result():
    value = text()
    assert "preexisting_repair_installer_state" in value
    assert "repair_cache_staged_for_acceptance" in value
    assert "repair_cache_original_state_restored" in value
    assert "Runtime-aware signed-set lifecycle acceptance: PASS" in value


def test_no_secret_or_private_key_inputs_are_accepted():
    lowered = text().lower()
    assert "[string]$pin" not in lowered
    assert "[string]$password" not in lowered
    assert "[string]$pfx" not in lowered
    assert "private key" not in lowered
