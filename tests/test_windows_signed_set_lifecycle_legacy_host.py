from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "windows_signed_set_lifecycle_acceptance_legacy_host.ps1"


def text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_legacy_host_wrapper_is_ascii_safe_for_windows_powershell_51():
    raw = SCRIPT.read_bytes()
    assert all(byte < 128 for byte in raw)


def test_exact_release_and_runtime_identity_are_pinned():
    body = text()
    assert "f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a" in body
    assert "5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414" in body
    assert "EE1CFA955BA22F03C39C76B183D94CD37494582E" in body
    assert "Registered installation EXE is not the exact sealed 0.2.3 application." in body
    assert "Registered DisplayVersion mismatch." in body


def test_signed_release_is_verified_before_runtime_mutation():
    body = text()
    verifier = body.index("Invoke-ReleaseVerifier\n\n$registered")
    runtime_read = body.index("$runtimeBefore = @(Get-ExactLauncherProcesses")
    runtime_stop = body.index("Stop-ExactRuntime -ExpectedExe $exe")
    assert verifier < runtime_read < runtime_stop


def test_support_files_are_observed_not_required_or_executed():
    body = text()
    assert "$supportPaths = [ordered]@{" in body
    assert "build_manifest = (Join-Path $installRoot 'build_manifest.json')" in body
    assert "repair_installer = (Join-Path $installRoot 'Arvectum Proxy Launcher Repair.exe')" in body
    assert "uninstall_helper = (Join-Path $installRoot 'uninstall_helper.ps1')" in body
    assert "$supportStates[$entry.Key]" in body
    assert "$missingSupport += $entry.Key" in body
    # The old support files are never invoked. The only legacy executable invoked
    # before snapshot is the exact hash-pinned product EXE for recovery commands.
    assert "-FilePath $repair" not in body
    assert "-FilePath $manifestPath" not in body
    assert "-FilePath $uninstaller" not in body


def test_complete_install_tree_is_fingerprinted_and_restored_exactly():
    body = text()
    assert "function Get-InstallTreeFingerprint" in body
    assert "$treeBefore = Get-InstallTreeFingerprint -Root $installRoot" in body
    assert "$treeAfter = Get-InstallTreeFingerprint -Root $installRoot" in body
    assert "$treeAfterRuntime = Get-InstallTreeFingerprint -Root $installRoot" in body
    assert "owner_host_install_tree_restored_exact" in body
    assert "Legacy install tree byte-exact restoration: PASS" in body


def test_wrapper_snapshots_registration_state_shortcuts_and_run_values():
    body = text()
    assert "reg.exe" in body
    assert "export legacy uninstall registration" in body
    assert "restore legacy uninstall registration" in body
    assert "$oldMainRun = Get-RunValue $mainRunName" in body
    assert "$oldRecoveryRun = Get-RunValue $recoveryRunName" in body
    assert "$shortcutSnapshots" in body
    assert "Move-Item -LiteralPath $installRoot -Destination $installBackup" in body
    assert "Move-Item -LiteralPath $installBackup -Destination $installRoot" in body


def test_canonical_lifecycle_is_delegated_without_weakening_base_gate():
    body = text()
    assert "windows_signed_set_lifecycle_acceptance.ps1" in body
    assert "Invoke-BaseAcceptance" in body
    assert "Canonical exact signed-set lifecycle acceptance: PASS" in body
    assert "preexisting_registered_runtime_exact" in body
    assert "RUNTIME_EXACT_SUPPORT_DRIFT" in body
    assert "legacy_support_drift_accepted" in body
