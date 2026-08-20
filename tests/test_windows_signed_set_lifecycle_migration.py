from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "windows_signed_set_lifecycle_acceptance_migration.ps1"


def body() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_script_is_ascii_safe_for_windows_powershell_51():
    assert all(byte < 128 for byte in SCRIPT.read_bytes())


def test_signed_release_is_verified_before_legacy_runtime_or_host_mutation():
    text = body()
    verifier = text.index("Invoke-ReleaseVerifier\n\n$runtimeBefore")
    runtime_read = text.index("$runtimeBefore = @(Get-LegacyProcesses)")
    rescue_copy = text.index("Copy-Item -LiteralPath $installRoot -Destination $rescueInstall")
    process_stop = text.index("Stop-LegacyProcesses -Processes $runtimeBefore")
    install_move = text.index("Move-Item -LiteralPath $installRoot -Destination $workInstall")
    assert verifier < runtime_read < rescue_copy < process_stop < install_move


def test_legacy_exe_is_observed_but_not_required_to_match_sealed_bytes():
    text = body()
    assert "$legacyExeSha256 = Get-Sha256 $exe" in text
    assert "$legacyMatchesSealed = ($legacyExeSha256 -eq $ExpectedApplicationSha256)" in text
    assert "Legacy matches sealed" in text
    assert "LEGACY_NONSEALED_RUNTIME" in text
    assert "preexisting_exe_sha256" in text
    assert "preexisting_exe_matches_sealed" in text


def test_legacy_support_files_are_never_required_or_executed():
    text = body()
    for forbidden in (
        "Arvectum Proxy Launcher Repair.exe",
        "build_manifest.json",
        "upgrade_helper.ps1",
        "uninstall_helper.ps1",
        ".arvectum-install-owner",
    ):
        assert forbidden not in text
    assert "--stop" not in text
    assert "--rollback" not in text


def test_rescue_is_verified_before_process_termination():
    text = body()
    rescue_verify = text.index("Independent rescue install-tree copy verification failed.")
    rescue_registry = text.index("export rescue uninstall registration")
    rescue_armed = text.index('Write-Host "Independent rescue armed: $rescueRoot"')
    process_stop = text.index("Stop-LegacyProcesses -Processes $runtimeBefore")
    assert rescue_verify < rescue_registry < rescue_armed < process_stop


def test_partial_mutation_restore_is_armed_before_registry_and_run_changes():
    text = body()
    run_arm = text.index("$runRestoreArmed = $true")
    run_mutation = text.index("Set-RunValue $mainRunName $null", run_arm)
    registry_arm = text.index("$registryRestoreArmed = $true")
    registry_mutation = text.index("Remove-Item -LiteralPath $UserUninstallKey -Recurse -Force", registry_arm)
    shortcut_arm = text.index("$shortcutsRestoreArmed = $true")
    shortcut_mutation = text.index("Remove-Item -LiteralPath $shortcut", shortcut_arm)
    assert run_arm < run_mutation
    assert registry_arm < registry_mutation
    assert shortcut_arm < shortcut_mutation


def test_state_cleanup_only_occurs_after_canonical_test_started():
    text = body()
    base_started = text.index("$baseStarted = $true")
    invoke_base = text.index("Invoke-BaseAcceptance", base_started)
    finally_gate = text.index("if ($baseStarted) {", invoke_base)
    test_state_remove = text.index("Remove-Item -LiteralPath $stateRoot", finally_gate)
    state_restore = text.index("if ($stateIsolated) {", test_state_remove)
    assert base_started < invoke_base < finally_gate < test_state_remove < state_restore


def test_complete_install_and_state_trees_are_fingerprinted_and_restored():
    text = body()
    assert "function Get-TreeFingerprint" in text
    assert "$treeBefore = Get-TreeFingerprint $installRoot" in text
    assert "$stateBefore = if ($hadStateRoot) { Get-TreeFingerprint $stateRoot } else { $null }" in text
    assert "owner_host_install_tree_restored_exact" in text
    assert "owner_host_state_tree_restored_exact" in text
    assert "Legacy install tree restoration: BYTE-EXACT" in text


def test_runtime_restore_happens_only_after_tree_restoration():
    text = body()
    tree_validation = text.index("$treeRestored = $false")
    runtime_restore = text.index("$runtimeRestored = $false", tree_validation)
    restart = text.index("Start-LegacyRuntime", runtime_restore)
    assert tree_validation < runtime_restore < restart


def test_independent_rescue_is_persistent_until_success():
    text = body()
    rescue_root = text.index("$rescueRoot = Join-Path 'C:\\Arvectum\\Recovery'")
    pass_gate = text.index("if (-not $basePassed)")
    rescue_delete = text.index("Remove-Item -LiteralPath $rescueRoot", pass_gate)
    assert rescue_root < pass_gate < rescue_delete
