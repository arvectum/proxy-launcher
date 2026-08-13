from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReleaseScriptTests(unittest.TestCase):
    def read(self, name):
        return (ROOT / name).read_text(encoding="utf-8-sig")

    def test_installer_uses_documents_location_and_owner_marker(self):
        text = self.read("install.bat")
        self.assertIn(r"%USERPROFILE%\Documents\ArvectumProxyLauncher", text)
        uninstall = self.read("uninstall.ps1")
        self.assertIn(".arvectum-install-owner", uninstall)
        self.assertIn("ARVECTUM_PROXY_LAUNCHER_WINDOWS_RC2_1", uninstall)

    def test_installer_does_not_unconditionally_delete_same_named_task(self):
        text = self.read("install.bat")
        self.assertIn('uninstall.ps1" -Install', text)
        self.assertNotIn('schtasks /Delete', text)

    def test_python_fallback_installs_powershell_uninstaller(self):
        text = self.read("install.bat")
        self.assertIn("uninstall.ps1", text)

    def test_exe_installer_copies_install_instructions_and_requires_marker(self):
        text = self.read("install.bat")
        self.assertIn('-SourceDir "%~dp0."', text)
        self.assertIn('uninstall.ps1" -Install', text)
        uninstall = self.read("uninstall.ps1")
        self.assertIn('if ($Install)', uninstall)
        self.assertIn('Installer finalization failed', uninstall)
        self.assertIn("'INSTALL.txt'", uninstall)
        self.assertIn("'uninstall.ps1'", uninstall)

    def test_uninstaller_requires_owner_marker_before_recursive_remove(self):
        text = self.read("uninstall.ps1")
        marker_pos = text.index("ownership marker is missing")
        remove_pos = text.index("Remove-Item -LiteralPath $fullAppDir -Recurse -Force")
        self.assertLess(marker_pos, remove_pos)
        self.assertIn("ReparsePoint", text)
        self.assertIn("unexpected application directory", text)

    def test_uninstaller_keeps_rollback_before_recursive_remove(self):
        text = self.read("uninstall.ps1")
        rollback_pos = text.index("& $exe --rollback")
        remove_pos = text.index("Remove-Item -LiteralPath $fullAppDir -Recurse -Force")
        self.assertLess(rollback_pos, remove_pos)
        self.assertIn("Network restore is incomplete", text)

    def test_uninstaller_closes_only_processes_owned_by_exact_exe_path(self):
        text = self.read("uninstall.ps1")
        self.assertIn("Name='Arvectum Proxy Launcher.exe'", text)
        self.assertIn("GetFullPath($_.ExecutablePath) -ieq $exe", text)
        self.assertIn("Stop-Process -Id $process.ProcessId", text)

    def test_source_helper_bats_target_documents_install(self):
        for name in ("run_gui.bat", "start_proxy.bat", "stop_proxy.bat"):
            text = self.read(name)
            self.assertIn(r"%USERPROFILE%\Documents\ArvectumProxyLauncher", text)
            self.assertNotIn(r"%LOCALAPPDATA%\ArvectumProxyLauncher", text)

    def test_restore_helper_targets_documents_install(self):
        text = self.read("restore_network.bat")
        self.assertIn(r"%USERPROFILE%\Documents\ArvectumProxyLauncher", text)

    def test_release_version_is_visible_in_gui(self):
        core_text = self.read("proxy_core.py")
        gui_text = self.read("proxy_gui.py")
        self.assertIn('APP_VERSION = "RC2.1"', core_text)
        self.assertIn('APP_VERSION = core.APP_VERSION', gui_text)
        self.assertIn('ARVECTUM · %s · arvectum.com', gui_text)

    def test_gui_autostart_task_is_ownership_checked(self):
        text = self.read("proxy_gui.py")
        self.assertIn("_autostart_task_is_ours", text)
        self.assertIn("принадлежит другой команде", text)
        self.assertIn('["schtasks", "/Query", "/TN", TASK_NAME, "/XML"]', text)

    def test_recovery_run_value_is_ownership_checked(self):
        text = self.read("proxy_core.py")
        self.assertIn("refusing overwrite", text)
        self.assertIn("leaving it untouched", text)
        self.assertIn("_normalize_command(current)", text)

    def test_gui_contains_explicit_recovery_guidance(self):
        text = self.read("proxy_gui.py")
        self.assertIn("Предыдущий сеанс proxy завершился некорректно", text)
        self.assertIn("Восстановить настройки сети", text)
        self.assertIn('self.btn_restore.configure(style="Mint.TButton")', text)
        self.assertIn("Сеть восстановлена. Теперь можно снова включить прокси.", text)


if __name__ == "__main__":
    unittest.main()
