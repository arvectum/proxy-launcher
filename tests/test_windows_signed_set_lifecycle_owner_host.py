from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "windows_signed_set_lifecycle_acceptance_owner_host.ps1"


def text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_wrapper_exists_and_is_windows_powershell_51_safe_ascii():
    assert SCRIPT.is_file()
    assert all(byte < 128 for byte in SCRIPT.read_bytes())


def test_wrapper_accepts_only_exact_user_registered_installation():
    value = text()
    assert "$ExpectedVersion = '0.2.3'" in value
    assert "f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a" in value
    assert "5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414" in value
    assert "$registered.Count -ne 1 -or $registered[0] -cne $UserUninstallKey" in value
    assert "Registered installation EXE does not match" in value
    assert "cached repair installer does not match" in value
    assert "Registered DisplayVersion mismatch" in value


def test_wrapper_blocks_active_recovery_and_running_launcher():
    value = text()
    assert "Assert-NoRunningLauncher" in value
    assert "proxy_internet_backup.json" in value
    assert "proxy_env_backup.json" in value
    assert "Active network recovery backup exists" in value


def test_snapshot_is_complete_before_mutation():
    value = text()
    export_index = value.index("'reg.exe' -ArgumentList @('export'")
    armed_index = value.index("$restoreArmed = $true")
    first_move_index = value.index("Move-Item -LiteralPath $installRoot -Destination $installBackup")
    remove_registry_index = value.index("Remove-Item -LiteralPath $UserUninstallKey -Recurse -Force")
    assert export_index < armed_index < first_move_index < remove_registry_index
    assert "Copy-Item -LiteralPath $shortcut -Destination $backup" in value
    assert "$oldMainRun = Get-RunValue $mainRunName" in value
    assert "$oldRecoveryRun = Get-RunValue $recoveryRunName" in value


def test_wrapper_restores_registry_files_state_run_values_and_shortcuts():
    value = text()
    assert "Move-Item -LiteralPath $installBackup -Destination $installRoot" in value
    assert "Move-Item -LiteralPath $stateBackup -Destination $stateRoot" in value
    assert "Set-RunValue $mainRunName $oldMainRun" in value
    assert "Set-RunValue $recoveryRunName $oldRecoveryRun" in value
    assert "'reg.exe' -ArgumentList @('import'" in value
    assert "Copy-Item -LiteralPath $snapshot.Backup -Destination $snapshot.Original" in value
    assert "restored executable hash mismatch" in value
    assert "restored cached repair installer hash mismatch" in value


def test_wrapper_delegates_to_canonical_acceptance_and_preserves_evidence():
    value = text()
    assert "windows_signed_set_lifecycle_acceptance.ps1" in value
    assert "Invoke-BaseAcceptance" in value
    assert "preexisting_registered_install" in value
    assert "owner_host_snapshot_restored" in value
    assert "Canonical signed-set lifecycle acceptance: PASS" in value


def test_wrapper_never_accepts_secret_material():
    lowered = text().lower()
    assert "[string]$pin" not in lowered
    assert "[string]$password" not in lowered
    assert "[string]$pfx" not in lowered
    assert "private key" not in lowered
