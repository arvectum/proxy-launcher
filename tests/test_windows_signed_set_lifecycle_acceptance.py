from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "windows_signed_set_lifecycle_acceptance.ps1"


def text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_script_exists_and_is_windows_powershell_51_safe_ascii():
    assert SCRIPT.is_file()
    raw = SCRIPT.read_bytes()
    assert all(byte < 128 for byte in raw)


def test_script_pins_exact_published_release_identity():
    value = text()
    assert "$ExpectedVersion = '0.2.3'" in value
    assert "$ExpectedTag = 'v0.2.3-ru.2'" in value
    assert "$ExpectedCommit = '47823585c42da54ab51dc2246583dc24d74d4ba6'" in value
    assert "$ExpectedSignerThumbprint = 'EE1CFA955BA22F03C39C76B183D94CD37494582E'" in value
    assert "62d313547b4d8c2c8e6951d6cd866bb954fdf199ad7650063c8ed3bfbc455801" in value
    assert "5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414" in value


def test_script_requires_publish_gate_and_verifies_signed_set_before_and_after():
    value = text()
    assert "if ([string]$decision.decision -ne 'PUBLISH')" in value
    assert "Invoke-ReleaseVerifier 'preflight signed-set verification'" in value
    assert "Invoke-ReleaseVerifier 'post-lifecycle signed-set verification'" in value
    assert "Portable ZIP changed during lifecycle acceptance." in value
    assert "Installer changed during lifecycle acceptance." in value


def test_script_fails_closed_over_registered_installation():
    value = text()
    assert "function Assert-NoRegisteredInstall" in value
    assert "{6A5A0706-4015-4EAF-BFA1-25EF435C9E1B}_is1" in value
    assert "Refusing destructive acceptance over an installed instance." in value


def test_script_isolates_and_restores_existing_portable_state():
    value = text()
    assert "$hadInstallRoot = Test-Path -LiteralPath $installRoot" in value
    assert "$hadStateRoot = Test-Path -LiteralPath $stateRoot" in value
    assert "Move-Item -LiteralPath $installRoot -Destination $installBackup" in value
    assert "Move-Item -LiteralPath $stateRoot -Destination $stateBackup" in value
    assert "Move-Item -LiteralPath $installBackup -Destination $installRoot" in value
    assert "Move-Item -LiteralPath $stateBackup -Destination $stateRoot" in value
    assert "$evidence.environment_restored = $true" in value


def test_restore_guard_is_armed_before_first_host_mutation():
    value = text()
    guard_index = value.index("$testEnvironmentActive = $true")
    install_move_index = value.index("Move-Item -LiteralPath $installRoot -Destination $installBackup")
    state_move_index = value.index("Move-Item -LiteralPath $stateRoot -Destination $stateBackup")
    registry_clear_index = value.index("Set-RunValue $mainRunName $null")
    assert guard_index < install_move_index
    assert guard_index < state_move_index
    assert guard_index < registry_clear_index
    assert "$testEnvironmentActive = $false" not in value


def test_script_covers_fresh_repair_recovery_uninstall_and_smoke():
    value = text()
    assert "=== Phase 1: fresh install and smoke ===" in value
    assert "Assert-InstallMode $installLog 'INSTALL'" in value
    assert "=== Phase 2: same-version repair path ===" in value
    assert "Assert-InstallMode $installLog 'REPAIR'" in value
    assert "=== Phase 3: corruption recovery through cached repair ===" in value
    assert "damaged-binary-for-production-lifecycle-acceptance" in value
    assert "=== Phase 4: uninstall ownership boundaries ===" in value
    assert "Invoke-Status" in value


def test_cached_repair_must_be_exact_signed_installer_copy():
    value = text()
    assert "Cached repair installer does not match the signed production installer." in value
    assert "Cached repair installer changed before recovery." in value
    assert "(Get-Sha256 $repair) -ne $ExpectedSetupSha256" in value


def test_persistent_config_and_foreign_autostart_boundaries_are_proven():
    value = text()
    assert "acceptance_canary" in value
    assert "Same-version repair modified proxy settings." in value
    assert "Recovery modified proxy settings." in value
    assert "Uninstall modified proxy settings." in value
    assert "Uninstall modified foreign recovery autostart." in value
    assert "$evidence.phases.user_configuration_preservation = 'PASS'" in value
    assert "$evidence.phases.foreign_autostart_preservation = 'PASS'" in value


def test_evidence_is_written_outside_signed_release_directory():
    value = text()
    assert "$EvidencePath = $ReleaseDirectory + '.lifecycle-acceptance.json'" in value
    assert "Set-Content -LiteralPath $EvidencePath" in value
    assert "Remove-Item -LiteralPath $ReleaseDirectory" not in value


def test_script_never_accepts_secret_or_private_key_material():
    lowered = text().lower()
    assert "[string]$pin" not in lowered
    assert "[string]$password" not in lowered
    assert "[string]$pfx" not in lowered
    assert "private key" not in lowered
