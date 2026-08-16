import os
import tempfile
import unittest
from unittest import mock

import proxy_core


class ForeignProxyProtectionTests(unittest.TestCase):
    """APL-REC-004 — prove recovery never claims or deletes foreign proxy state."""

    def test_exact_pac_ownership_rejects_foreign_variants(self):
        settings = {"local_pac_port": 8082, "pac_path": "/proxy.pac"}

        self.assertTrue(
            proxy_core._exact_arvectum_pac_url(
                "http://127.0.0.1:8082/proxy.pac", settings=settings
            )
        )
        for foreign in (
            "http://127.0.0.1:8082/proxy.pac?owner=foreign",
            "http://127.0.0.1:8082/proxy.pac#foreign",
            "http://localhost:8082/proxy.pac",
            "http://127.0.0.1:8083/proxy.pac",
            "http://127.0.0.1:8082/foreign.pac",
            "https://127.0.0.1:8082/proxy.pac",
            "http://user@127.0.0.1:8082/proxy.pac",
        ):
            with self.subTest(foreign=foreign):
                self.assertFalse(
                    proxy_core._exact_arvectum_pac_url(foreign, settings=settings)
                )

    def test_foreign_recovery_run_value_is_not_deleted_or_replaced(self):
        foreign = '"C:\\OtherProxy\\proxy-agent.exe" --start'

        with mock.patch.object(proxy_core, "is_windows", return_value=True), \
             mock.patch.object(proxy_core, "_get_recovery_run_value", return_value=foreign), \
             mock.patch.object(proxy_core, "_delete_run_value") as delete_value, \
             mock.patch.object(proxy_core, "_set_recovery_run_value") as set_value:
            self.assertTrue(proxy_core._enable_recovery_autostart())

        delete_value.assert_not_called()
        set_value.assert_not_called()

    def test_misleading_arvectum_substring_does_not_grant_run_ownership(self):
        commands = (
            '"C:\\Foreign\\Arvectum Proxy Launcher.exe.bak" --start',
            '"C:\\Foreign\\Arvectum Proxy Launcher.exe" --start',
            'powershell -Command "Arvectum Proxy Launcher.exe --start"',
            '"C:\\Foreign\\restore_network.bat"',
        )

        with mock.patch.object(
            proxy_core,
            "_known_legacy_recovery_dirs",
            return_value={os.path.normcase(os.path.realpath("C:\\Owned"))},
        ):
            for command in commands:
                with self.subTest(command=command):
                    self.assertEqual(
                        proxy_core.classify_recovery_autostart(command),
                        proxy_core._RECOVERY_FOREIGN,
                    )
                    self.assertFalse(proxy_core.is_owned_arvectum_start_command(command))

    def test_missing_backup_makes_wininet_restore_a_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = os.path.join(tmp, "proxy_internet_backup.json")
            with mock.patch.object(proxy_core, "_internet_backup_path", return_value=missing), \
                 mock.patch.object(proxy_core, "_reg_set") as reg_set, \
                 mock.patch.object(proxy_core, "_reg_del") as reg_del:
                self.assertTrue(proxy_core._restore_internet_backup())

            reg_set.assert_not_called()
            reg_del.assert_not_called()

    def test_invalid_backup_makes_wininet_restore_a_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid = os.path.join(tmp, "proxy_internet_backup.json")
            with open(invalid, "w", encoding="utf-8") as stream:
                stream.write('{"AutoConfigURL": {"exists": true}}')

            with mock.patch.object(proxy_core, "_internet_backup_path", return_value=invalid), \
                 mock.patch.object(proxy_core, "_reg_set") as reg_set, \
                 mock.patch.object(proxy_core, "_reg_del") as reg_del:
                self.assertTrue(proxy_core._restore_internet_backup())

            reg_set.assert_not_called()
            reg_del.assert_not_called()

    def test_foreign_pac_is_never_orphan_cleanup_candidate(self):
        foreign_values = {
            "AutoConfigURL": {
                "exists": True,
                "value": "http://127.0.0.1:9090/company-proxy.pac",
            }
        }
        with mock.patch.object(proxy_core, "is_windows", return_value=True), \
             mock.patch.object(proxy_core, "state_migration_blocked", return_value=False), \
             mock.patch.object(proxy_core, "_read_internet_settings", return_value=foreign_values), \
             mock.patch.object(proxy_core, "proxy_listener_active", return_value=False), \
             mock.patch.object(proxy_core, "is_running", return_value=False), \
             mock.patch.object(proxy_core, "_any_known_internet_backup_exists", return_value=False), \
             mock.patch.object(proxy_core, "canonical_install_exe", return_value=None), \
             mock.patch.object(proxy_core, "_reg_del") as reg_del:
            self.assertFalse(proxy_core.orphaned_arvectum_pac())
            self.assertFalse(proxy_core.clear_orphaned_arvectum_pac())

        reg_del.assert_not_called()

    def test_foreign_recovery_run_value_survives_disable(self):
        foreign = '"C:\\CorporateProxy\\recovery.exe" --repair'

        class FakeKey:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        fake_winreg = mock.Mock()
        fake_winreg.HKEY_CURRENT_USER = object()
        fake_winreg.KEY_QUERY_VALUE = 1
        fake_winreg.KEY_SET_VALUE = 2
        fake_winreg.OpenKey.return_value = FakeKey()
        fake_winreg.QueryValueEx.return_value = (foreign, 1)

        with mock.patch.object(proxy_core, "is_windows", return_value=True), \
             mock.patch.dict("sys.modules", {"winreg": fake_winreg}):
            self.assertTrue(proxy_core._disable_recovery_autostart())

        fake_winreg.DeleteValue.assert_not_called()


if __name__ == "__main__":
    unittest.main()
