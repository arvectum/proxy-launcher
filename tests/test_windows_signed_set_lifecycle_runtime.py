from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "windows_signed_set_lifecycle_acceptance_runtime.ps1"


def text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_runtime_wrapper_exists_and_is_windows_powershell_51_safe_ascii():
    assert SCRIPT.is_file()
    raw = SCRIPT.read_bytes()
    assert all(byte < 128 for byte in raw)


def test_exact_registered_install_is_validated_before_runtime_quiesce():
    value = text()
    exe_hash_check = "if ((Get-Sha256 $exe) -ne $ExpectedApplicationSha256)"
    repair_hash_check = "if ((Get-Sha256 $repair) -ne $ExpectedSetupSha256)"
    quiesce_call = "Stop-ExactRuntime -ExpectedExe $exe"
    assert exe_hash_check in value
    assert repair_hash_check in value
    assert quiesce_call in value
    assert value.index(exe_hash_check) < value.index(quiesce_call)
    assert value.index(repair_hash_check) < value.index(quiesce_call)


def test_only_exact_governed_process_paths_can_be_touched():
    value = text()
    assert "function Get-ExactLauncherProcesses" in value
    assert "Test-ExactPath $path $ExpectedExe" in value
    assert "same-named foreign launcher process is running and will not be touched" in value
    assert "Stop-Process -Id ([int]$process.ProcessId) -Force" in value


def test_runtime_uses_product_stop_and_rollback_before_force_quiesce():
    value = text()
    assert "-ArgumentList @('--stop')" in value
    assert "-ArgumentList @('--rollback')" in value
    assert "Get-RecoveryFiles" in value
    assert "Network recovery state remains after runtime quiesce" in value
    assert value.index("-ArgumentList @('--stop')") < value.index("Stop-Process -Id")


def test_core_and_gui_running_state_are_captured_separately():
    value = text()
    assert "function Test-CoreProcess" in value
    assert "--start" in value
    assert "$wasRuntimeRunning = ($runtimeBefore.Count -gt 0)" in value
    assert "$wasCoreRunning = ($coreBefore.Count -gt 0)" in value
    assert "$wasGuiRunning = ($guiBefore.Count -gt 0)" in value


def test_original_core_and_gui_state_are_restored_after_owner_host_acceptance():
    value = text()
    assert "function Start-OriginalRuntime" in value
    assert "Start-Process -FilePath $exe -ArgumentList @('--start')" in value
    assert "Start-Process -FilePath $exe -WorkingDirectory $installRoot" in value
    assert "Start-OriginalRuntime -CoreWasRunning $wasCoreRunning -GuiWasRunning $wasGuiRunning" in value
    assert "Original runtime state restored: PASS" in value


def test_owner_host_snapshot_wrapper_remains_the_authoritative_lifecycle_path():
    value = text()
    assert "windows_signed_set_lifecycle_acceptance_owner_host.ps1" in value
    assert "Invoke-OwnerHostAcceptance" in value
    assert "Owner-host signed-set lifecycle acceptance: PASS" in value


def test_runtime_evidence_records_quiesce_and_restore():
    value = text()
    assert "owner_host_runtime_was_running" in value
    assert "owner_host_core_was_running" in value
    assert "owner_host_gui_was_running" in value
    assert "owner_host_runtime_quiesced" in value
    assert "owner_host_runtime_restored" in value
    assert "$evidence.result = 'BLOCK'" in value


def test_transient_maintenance_processes_fail_closed_before_quiesce():
    value = text()
    assert "function Test-MaintenanceProcess" in value
    assert "A launcher maintenance command is already running" in value
    assert value.index("A launcher maintenance command is already running") < value.index("Stop-ExactRuntime -ExpectedExe $exe")


def test_script_never_accepts_secret_or_private_key_material():
    lowered = text().lower()
    assert "[string]$pin" not in lowered
    assert "[string]$password" not in lowered
    assert "[string]$pfx" not in lowered
    assert "private key" not in lowered
