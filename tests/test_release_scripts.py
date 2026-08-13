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
        self.assertIn("ARVECTUM_PROXY_LAUNCHER_INSTALL_OWNER", uninstall)
        self.assertIn("ARVECTUM_PROXY_LAUNCHER_WINDOWS_RC2_1", uninstall)

    def test_owner_marker_migrates_without_breaking_legacy_uninstall(self):
        uninstall = self.read("uninstall.ps1")
        core = self.read("proxy_core.py")
        self.assertIn("ARVECTUM_PROXY_LAUNCHER_INSTALL_OWNER", uninstall)
        self.assertIn("legacyOwnerMarkerValue", uninstall)
        self.assertIn("_LEGACY_INSTALL_OWNER_VALUES", core)

    def test_install_documents_stable_state_locations_are_documented(self):
        text = self.read("INSTALL.txt")
        self.assertIn(r"%USERPROFILE%\Documents\ArvectumProxyLauncher", text)
        self.assertIn(r"%LOCALAPPDATA%\Arvectum\ProxyLauncher", text)

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
        self.assertIn('APP_VERSION = "0.2.1"', core_text)
        self.assertIn('APP_VERSION = core.APP_VERSION', gui_text)
        self.assertIn('ARVECTUM · %s · arvectum.com', gui_text)

    def test_windows_version_resource_is_required(self):
        build = self.read("build_exe.bat")
        version = self.read("version_info.txt")
        self.assertIn('--version-file "version_info.txt"', build)
        for value in ('ООО «Арвектум»', 'Arvectum Proxy Launcher', '0.2.1', '0.2.1.0'):
            self.assertIn(value, version)

    def test_inno_setup_delegates_safe_uninstall_and_blocks_unsafe_upgrade(self):
        text = self.read("ArvectumProxyLauncherSetup.iss")
        self.assertIn("Uninstallable=no", text)
        self.assertIn("QuietUninstallString", text)
        self.assertIn("uninstall.ps1", text)
        self.assertIn("UPDATE BLOCKED", text)
        self.assertIn("proxy_internet_backup.json", text)
        self.assertIn("ARVECTUM_PROXY_LAUNCHER_INSTALL_OWNER", text)
        self.assertIn("SaveStringToFile", text)
        self.assertIn("CloseApplications=yes", text)
        self.assertIn("CloseApplicationsFilter=Arvectum Proxy Launcher.exe", text)
        self.assertIn("function CloseOwnedLauncher", text)
        self.assertIn("$_.ExecutablePath", text)
        self.assertIn("Get-CimInstance Win32_Process", text)

    def test_uninstaller_removes_own_installed_apps_entry_and_start_menu_shortcut(self):
        text = self.read("uninstall.ps1")
        self.assertIn("ArvectumProxyLauncher'", text)
        self.assertIn("$startMenuShortcut", text)
        self.assertIn("Remove-Item -LiteralPath $arpKey", text)

    def test_gui_autostart_uses_owned_per_user_run_value(self):
        text = self.read("proxy_gui.py")
        self.assertIn("AUTOSTART_RUN_VALUE", text)
        self.assertIn("AUTOSTART_RUN_PATH", text)
        self.assertIn("_autostart_run_is_ours", text)
        self.assertIn("winreg.SetValueEx", text)
        self.assertIn("_autostart_task_is_ours", text)
        self.assertIn("принадлежит другой команде", text)

    def test_recovery_run_value_is_ownership_checked(self):
        text = self.read("proxy_core.py")
        self.assertIn("LEGACY_ARVECTUM", text)
        self.assertIn("conflicts with a foreign command", text)
        self.assertIn("leaving it untouched", text)
        self.assertIn("classify_recovery_autostart", text)

    def test_gui_contains_explicit_recovery_guidance(self):
        text = self.read("proxy_gui.py")
        self.assertIn("Предыдущий сеанс proxy завершился некорректно", text)
        self.assertIn("Восстановить настройки сети", text)
        self.assertIn('self.btn_restore.configure(style="Mint.TButton")', text)
        self.assertIn("Сеть восстановлена. Теперь можно снова включить прокси.", text)

    def test_gui_has_targeted_orphan_pac_action(self):
        text = self.read("proxy_gui.py")
        self.assertIn("ОБНАРУЖЕН СТАРЫЙ PAC ARVECTUM", text)
        self.assertIn("Удалить старый PAC и продолжить", text)
        self.assertIn("clear_orphaned_arvectum_pac", text)
        self.assertIn("Остальные настройки Windows не изменялись", text)

    def test_main_header_is_text_based_and_has_no_banner_or_separator(self):
        text = self.read("proxy_gui.py")
        launcher = text[text.index("class Launcher:"):]
        self.assertIn('text=APP_NAME, bg=NAVY, fg=MINT', launcher)
        self.assertIn('font=B["font_brand"]', launcher)
        self.assertNotIn('_load_photo("arvectum-banner.png"', launcher)
        self.assertNotIn('tk.Frame(root, bg=MINT, height=3)', launcher)

    def test_main_controls_have_clear_visual_hierarchy(self):
        text = self.read("proxy_gui.py")
        self.assertIn('style.configure("Navy.TButton"', text)
        self.assertIn('text="Проверить соединение"', text)
        self.assertIn('text="Настройки и сервис"', text)
        self.assertIn('text="Состояние"', text)


if __name__ == "__main__":
    unittest.main()
