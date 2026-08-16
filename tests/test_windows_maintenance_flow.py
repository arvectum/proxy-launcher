from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WindowsMaintenanceFlowTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8-sig")

    def test_repair_is_cached_and_removed_with_the_install(self):
        iss = self.read("installer/ArvectumProxyLauncher.iss")
        self.assertIn('RepairExeName "Arvectum Proxy Launcher Repair.exe"', iss)
        self.assertIn("procedure CacheRepairInstaller", iss)
        self.assertIn("{srcexe}", iss)
        self.assertIn('Repair Arvectum Proxy Launcher', iss)
        self.assertIn('Type: files; Name: "{app}\\{#RepairExeName}"', iss)
        self.assertIn("SuppressibleMsgBox(ErrorText", iss)

    def test_repair_does_not_execute_damaged_exe_when_no_recovery_is_pending(self):
        helper = self.read("installer/upgrade_helper.ps1")
        rollback = helper[helper.index("function Invoke-PreviousRollback"):helper.index("try {\n  Write-InstallLog")]
        self.assertIn("$backups = @(Get-RecoveryBackups)", rollback)
        self.assertIn("if ($backups.Count -gt 0)", rollback)
        self.assertIn("& $ExistingExe --stop", rollback)
        self.assertIn("Stop-OwnedProcess $ExistingExe", rollback)

    def test_repair_fails_closed_if_backups_exist_without_recovery_executable(self):
        helper = self.read("installer/upgrade_helper.ps1")
        self.assertIn("recovery backups remain but the installed Launcher executable is missing", helper)
        self.assertIn("repair is blocked until network recovery can be proven", helper)

    def test_repair_cleans_only_operational_stale_state(self):
        helper = self.read("installer/upgrade_helper.ps1")
        self.assertIn("function Clear-StaleMaintenanceState", helper)
        self.assertIn("proxy_core.pid", helper)
        self.assertIn("stale owned recovery Run value removed", helper)
        self.assertIn("stale transactional artifact removed", helper)
        self.assertNotIn("Remove-Item -LiteralPath (Join-Path $StateRoot 'proxy_settings.json')", helper)
        self.assertNotIn("Remove-Item -LiteralPath (Join-Path $StateRoot 'no_proxy.txt')", helper)

    def test_uninstall_requires_proven_network_recovery(self):
        helper = self.read("installer/uninstall_helper.ps1")
        self.assertIn("Get-RecoveryBackups", helper)
        self.assertIn("Network rollback cannot be proven", helper)
        self.assertIn("recovery backups exist but the installed Launcher executable is missing", helper)
        self.assertIn("$rollback.ExitCode", helper)
        self.assertIn("recovery backups remain and uninstall stopped safely", helper)

    def test_uninstall_removes_only_owned_startup_state(self):
        helper = self.read("installer/uninstall_helper.ps1")
        self.assertIn("function Test-OwnedStartCommand", helper)
        self.assertIn("function Remove-OwnedRunValue", helper)
        self.assertIn("foreign or unknown Run value preserved", helper)
        self.assertIn("function Remove-OwnedLegacyTask", helper)
        self.assertIn("//t:Actions/t:Exec", helper)
        self.assertIn("foreign or unknown legacy scheduled task preserved", helper)
        self.assertNotIn("taskkill", helper.lower())

    def test_absent_legacy_task_is_captured_as_native_exit_code(self):
        helper = self.read("installer/uninstall_helper.ps1")
        self.assertIn("function Invoke-NativeCapture", helper)
        self.assertIn("RedirectStandardOutput", helper)
        self.assertIn("RedirectStandardError", helper)
        self.assertIn("legacy scheduled task absent; nothing to remove", helper)
        self.assertIn("$query.ExitCode -ne 0", helper)
        self.assertNotIn("/XML 2>$null", helper)

    def test_windows_ci_repairs_corruption_and_checks_config_preservation(self):
        workflow = self.read(".github/workflows/windows-installer.yml")
        e2e = self.read("qa/windows_rc_e2e.ps1")

        # The workflow must execute the governed lifecycle harness instead of
        # duplicating the maintenance test implementation inline in YAML.
        self.assertIn("./qa/windows_rc_e2e.ps1", workflow)
        self.assertIn("out\\windows-rc-e2e.json", workflow)

        # APL-WIN-009 repair/uninstall invariants remain mandatory under the
        # broader APL-WIN-012 RC lifecycle harness.
        self.assertIn("damaged-binary-for-apl-win-012-repair", e2e)
        self.assertIn("Arvectum Proxy Launcher Repair.exe", e2e)
        self.assertIn('"config_version":1', e2e)
        self.assertIn("Get-FileHash -LiteralPath $settings -Algorithm SHA256", e2e)
        self.assertIn("repair left stale PID file", e2e)
        self.assertIn("repair modified persistent proxy settings", e2e)
        self.assertIn("uninstall left owned main autostart value", e2e)
        self.assertIn("uninstall modified foreign recovery autostart value", e2e)
        self.assertIn("uninstall modified persistent no-proxy rules", e2e)

    def test_contract_document_is_present(self):
        contract = self.read("APL-WIN-009_WINDOWS_UNINSTALL_REPAIR.md")
        self.assertIn("Status: **implemented**", contract)
        self.assertIn("fail-closed", contract)
        self.assertIn("proxy_settings.json", contract)
        self.assertIn("no_proxy.txt", contract)
        self.assertIn("cached repair", contract.lower())


if __name__ == "__main__":
    unittest.main()
