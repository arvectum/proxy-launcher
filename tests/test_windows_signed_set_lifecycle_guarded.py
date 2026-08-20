from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "windows_signed_set_lifecycle_acceptance_guarded.ps1"


def text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_guard_is_ascii_safe_for_windows_powershell_51():
    assert all(byte < 128 for byte in SCRIPT.read_bytes())


def test_guard_arms_rescue_before_inner_lifecycle():
    body = text()
    copy_install = body.index("Copy-Item -LiteralPath $installRoot -Destination $rescueInstall")
    verify_rescue = body.index("Independent rescue install snapshot fingerprint mismatch.")
    inner_call = body.index("& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $inner", verify_rescue)
    assert copy_install < verify_rescue < inner_call


def test_guard_pins_exact_owner_host_executable_before_rescue():
    body = text()
    assert "f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a" in body
    assert "Registered owner-host EXE is not exact before rescue arming." in body
    assert "DisplayVersion mismatch before rescue arming." in body


def test_failed_inner_run_restores_complete_owner_host_surface():
    body = text()
    assert "Stop-ExactPathProcesses $exe" in body
    assert "restore rescue install" in body
    assert "restore rescue state" in body
    assert "restore rescue registration" in body
    assert "restore Run values" in body
    assert "restore shortcut" in body
    assert "Restore-RuntimeShape $runtimeBefore" in body


def test_guard_requires_byte_exact_install_tree_after_success_or_rescue():
    body = text()
    assert "Same-Fingerprint $treeBefore $after" in body
    assert "Same-Fingerprint $treeBefore $restored" in body
    assert "Pre-run install tree fingerprint preserved: PASS" in body


def test_guard_records_rescue_evidence():
    body = text()
    assert "owner_host_rescue_armed" in body
    assert "owner_host_rescue_used" in body
    assert "owner_host_rescue_install_tree_sha256" in body
    assert "owner_host_rescue_restored" in body
