from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "windows_app_control_local_gate.ps1"


def _text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_local_gate_is_explicitly_isolated_and_windows_11_only():
    text = _text()
    assert "IsolatedAcceptanceEnvironment" in text
    assert "disposable/isolated Windows 11" in text
    assert "Build -lt 22000" in text
    assert "Assert-Administrator" in text
    assert "Assert-CleanAcceptanceState" in text


def test_local_gate_never_deploys_or_removes_app_control_policy():
    text = _text()
    # Documentation may name the forbidden commands, but the script must never
    # execute them through CiTool, Start-Process, cmd or PowerShell invocation.
    lowered = text.lower()
    forbidden_execution_shapes = (
        "& $citool --update-policy",
        "& $citool --remove-policy",
        "start-process -filepath $citool",
        "start-process -filepath 'citool",
        'start-process -filepath "citool',
    )
    for shape in forbidden_execution_shapes:
        assert shape not in lowered
    assert "VerifiedAndReputablePolicyState" not in text
    assert "Set-RuleOption" not in text
    assert "Disable-WindowsOptionalFeature" not in text


def test_prepare_phase_requires_reference_full_hash_and_does_not_claim_acceptance():
    text = _text()
    assert "-Mode ReferenceFullHash" in text
    assert "result = 'PREPARED'" in text
    assert "Policy deployment: NOT PERFORMED" in text
    assert "windows_app_control_enterprise_trust_pack.ps1" in text


def test_enforced_phase_proves_real_base_and_supplemental_policy_state():
    text = _text()
    assert "Get-AppControlPolicies" in text
    assert "-lp -json" in text
    assert "base_policy_enforced" in text
    assert "supplemental_policy_active" in text
    assert "is_enforced" in text
    assert "is_on_disk" in text
    assert "No simulated App Control acceptance is allowed" in text


def test_enforced_phase_exercises_setup_gui_core_pac_and_rollback():
    text = _text()
    assert "setup_under_enforcement" in text
    assert "first_gui_launch" in text
    assert "--start" in text
    assert "--status" in text
    assert "RUNNING" in text
    assert "system proxy:\\s*ENABLED" in text
    assert "http://127.0.0.1:8082/proxy.pac" in text
    assert "FindProxyForURL" in text
    assert "AutoConfigURL" in text
    assert "--rollback" in text
    assert "network settings restored" in text


def test_enforced_phase_runs_canonical_repair_uninstall_lifecycle():
    text = _text()
    assert "windows_signed_set_lifecycle_acceptance.ps1" in text
    assert "repair_corruption_uninstall_lifecycle" in text
    assert "environment_restored" in text


def test_enforced_phase_records_code_integrity_and_fails_on_arvectum_3077_blocks():
    text = _text()
    assert "Microsoft-Windows-CodeIntegrity/Operational" in text
    assert "3077" in text
    assert "arvectum_3077_block_events" in text
    assert "no_arvectum_enforcement_blocks" in text


def test_pass_requires_app_control_to_remain_enforced():
    text = _text()
    assert "app_control_remained_enforced" in text
    assert "APL-WIN-014 real App Control for Business acceptance: PASS" in text
