import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import proxy_core as core
import recovery_autostart


class _Key:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeWinreg:
    HKEY_CURRENT_USER = object()
    KEY_SET_VALUE = 1
    KEY_QUERY_VALUE = 2
    REG_SZ = 1

    def __init__(self, values=None):
        self.values = dict(values or {})
        self.set_calls = []
        self.delete_calls = []

    def OpenKey(self, *args, **kwargs):
        return _Key()

    def CreateKey(self, *args, **kwargs):
        return _Key()

    def QueryValueEx(self, key, name):
        if name not in self.values:
            raise FileNotFoundError(name)
        return self.values[name], self.REG_SZ

    def SetValueEx(self, key, name, reserved, typ, value):
        self.values[name] = value
        self.set_calls.append((name, value))

    def DeleteValue(self, key, name):
        if name not in self.values:
            raise FileNotFoundError(name)
        del self.values[name]
        self.delete_calls.append(name)


class RecoveryAutostartOwnershipTests(unittest.TestCase):
    def test_slice9_functions_are_owned_by_canonical_module(self):
        for name in (
            "_self_start_command",
            "_normalize_command",
            "_known_legacy_recovery_dirs",
            "_recovery_command_target",
            "_is_temporary_arvectum_start",
            "_is_proven_legacy_arvectum_start",
            "_delete_run_value",
            "repair_portable_run_entries",
            "classify_recovery_autostart",
            "is_owned_arvectum_start_command",
            "_recovery_legacy_process_active",
            "_get_recovery_run_value",
            "_set_recovery_run_value",
            "_enable_recovery_autostart",
            "_disable_recovery_autostart",
        ):
            self.assertEqual(getattr(core, name).__module__, "recovery_autostart")

    def test_recovery_constants_preserve_sealed_values(self):
        self.assertEqual(core._RECOVERY_RUN_VALUE, "ArvectumProxyLauncherRecovery")
        self.assertEqual(core._RECOVERY_CURRENT_OWNED, "CURRENT_OWNED")
        self.assertEqual(core._RECOVERY_LEGACY_ARVECTUM, "LEGACY_ARVECTUM")
        self.assertEqual(core._RECOVERY_FOREIGN, "FOREIGN")
        self.assertEqual(core._RECOVERY_MISSING, "MISSING")

    def test_command_parser_requires_an_explicit_quoted_target(self):
        target, args = core._recovery_command_target(
            '"C:/Owned/Arvectum Proxy Launcher.exe" --start'
        )
        self.assertTrue(target.endswith(os.path.normpath("C:/Owned/Arvectum Proxy Launcher.exe")))
        self.assertEqual(args, "--start")
        for command in (
            "C:/Owned/Arvectum Proxy Launcher.exe --start",
            'powershell -Command "Arvectum Proxy Launcher.exe --start"',
            "",
            None,
        ):
            with self.subTest(command=command):
                self.assertEqual(core._recovery_command_target(command), (None, ""))

    def test_temporary_start_recognition_is_exact(self):
        with tempfile.TemporaryDirectory() as td:
            temp_root = Path(td) / "Temp"
            temp_root.mkdir()
            launcher = temp_root / "zip" / core._LAUNCHER_EXE_NAME
            launcher.parent.mkdir()
            with mock.patch.object(core, "_temporary_roots", return_value=[str(temp_root)]):
                self.assertTrue(core._is_temporary_arvectum_start('"%s" --start' % launcher))
                self.assertFalse(core._is_temporary_arvectum_start('"%s" --status' % launcher))
                self.assertFalse(
                    core._is_temporary_arvectum_start('"%s.evil" --start' % launcher)
                )

    def test_classification_accepts_only_current_or_strict_legacy_shapes(self):
        legacy_dir = os.path.normcase(os.path.realpath("C:/Owned/ArvectumProxyLauncher"))
        current = '"C:/Current/Arvectum Proxy Launcher.exe" --start'
        legacy = '"C:/Owned/ArvectumProxyLauncher/Arvectum Proxy Launcher.exe" --start'
        batch = '"C:/Owned/ArvectumProxyLauncher/restore_network.bat"'
        with mock.patch.object(core, "_self_start_command", return_value=current), \
             mock.patch.object(core, "_known_legacy_recovery_dirs", return_value={legacy_dir}), \
             mock.patch.object(core, "_is_temporary_arvectum_start", return_value=False):
            self.assertEqual(core.classify_recovery_autostart(None), core._RECOVERY_MISSING)
            self.assertEqual(core.classify_recovery_autostart(current), core._RECOVERY_CURRENT_OWNED)
            self.assertEqual(core.classify_recovery_autostart(legacy), core._RECOVERY_LEGACY_ARVECTUM)
            self.assertEqual(core.classify_recovery_autostart(batch), core._RECOVERY_LEGACY_ARVECTUM)
            for foreign in (
                '"C:/Owned/ArvectumProxyLauncher/Arvectum Proxy Launcher.exe" --stop',
                '"C:/Owned/ArvectumProxyLauncher/restore_network.bat" --force',
                '"C:/Other/Arvectum Proxy Launcher.exe" --start',
                '"C:/Owned/ArvectumProxyLauncher/Arvectum Proxy Launcher.exe.evil" --start',
            ):
                with self.subTest(foreign=foreign):
                    self.assertEqual(
                        core.classify_recovery_autostart(foreign),
                        core._RECOVERY_FOREIGN,
                    )

    def test_release_directory_form_is_strictly_proven_legacy(self):
        command = (
            '"C:/Downloads/arvectum-proxy-launcher-windows-0.2.3/'
            'Arvectum Proxy Launcher.exe" --start'
        )
        with mock.patch.object(core, "_known_legacy_recovery_dirs", return_value=set()), \
             mock.patch.object(core, "_is_temporary_arvectum_start", return_value=False):
            self.assertTrue(core._is_proven_legacy_arvectum_start(command))
            self.assertTrue(core.is_owned_arvectum_start_command(command))

    def test_owned_start_predicate_rejects_substring_and_wrong_arguments(self):
        current = '"C:/Current/Arvectum Proxy Launcher.exe" --start'
        with mock.patch.object(core, "_self_start_command", return_value=current), \
             mock.patch.object(core, "_known_legacy_recovery_dirs", return_value=set()), \
             mock.patch.object(core, "_is_temporary_arvectum_start", return_value=False):
            self.assertTrue(core.is_owned_arvectum_start_command(current))
            self.assertFalse(
                core.is_owned_arvectum_start_command(
                    '"C:/Current/Arvectum Proxy Launcher.exe.evil" --start'
                )
            )
            self.assertFalse(
                core.is_owned_arvectum_start_command(
                    '"C:/Current/Arvectum Proxy Launcher.exe" --status'
                )
            )

    def test_enable_removes_only_owned_recovery_values(self):
        for classification in (
            core._RECOVERY_CURRENT_OWNED,
            core._RECOVERY_LEGACY_ARVECTUM,
        ):
            with self.subTest(classification=classification), \
                 mock.patch.object(core, "is_windows", return_value=True), \
                 mock.patch.object(core, "_get_recovery_run_value", return_value="owned"), \
                 mock.patch.object(core, "classify_recovery_autostart", return_value=classification), \
                 mock.patch.object(core, "_delete_run_value", return_value=True) as delete:
                self.assertTrue(recovery_autostart._enable_recovery_autostart())
            delete.assert_called_once_with(core._RECOVERY_RUN_VALUE)

    def test_enable_never_overwrites_foreign_or_unreadable_recovery_state(self):
        logs = []
        with mock.patch.object(core, "is_windows", return_value=True), \
             mock.patch.object(core, "_get_recovery_run_value", return_value="foreign"), \
             mock.patch.object(core, "classify_recovery_autostart", return_value=core._RECOVERY_FOREIGN), \
             mock.patch.object(core, "_delete_run_value") as delete, \
             mock.patch.object(core, "_set_recovery_run_value") as write, \
             mock.patch.object(core, "_log", side_effect=logs.append):
            self.assertTrue(recovery_autostart._enable_recovery_autostart())
        delete.assert_not_called()
        write.assert_not_called()
        self.assertTrue(any("foreign command" in message for message in logs))

        with mock.patch.object(core, "is_windows", return_value=True), \
             mock.patch.object(core, "_get_recovery_run_value", return_value=False), \
             mock.patch.object(core, "classify_recovery_autostart") as classify, \
             mock.patch.object(core, "_delete_run_value") as delete:
            self.assertTrue(recovery_autostart._enable_recovery_autostart())
        classify.assert_not_called()
        delete.assert_not_called()

    def test_missing_recovery_value_is_a_safe_noop(self):
        with mock.patch.object(core, "is_windows", return_value=True), \
             mock.patch.object(core, "_get_recovery_run_value", return_value=None), \
             mock.patch.object(core, "classify_recovery_autostart", return_value=core._RECOVERY_MISSING), \
             mock.patch.object(core, "_delete_run_value") as delete:
            self.assertTrue(recovery_autostart._enable_recovery_autostart())
        delete.assert_not_called()

    def test_disable_deletes_current_or_temporary_and_preserves_foreign(self):
        current = '"C:/Current/Arvectum Proxy Launcher.exe" --start'
        for value, temporary, expected_deleted in (
            (current, False, True),
            ('"C:/Temp/Arvectum Proxy Launcher.exe" --start', True, True),
            ('"C:/Corporate/recovery.exe" --repair', False, False),
        ):
            fake = _FakeWinreg({core._RECOVERY_RUN_VALUE: value})
            with self.subTest(value=value), \
                 mock.patch.object(core, "is_windows", return_value=True), \
                 mock.patch.object(core, "_self_start_command", return_value=current), \
                 mock.patch.object(core, "_is_temporary_arvectum_start", return_value=temporary), \
                 mock.patch.dict(sys.modules, {"winreg": fake}), \
                 mock.patch.object(core, "_log"):
                self.assertTrue(recovery_autostart._disable_recovery_autostart())
            self.assertEqual(
                core._RECOVERY_RUN_VALUE in fake.delete_calls,
                expected_deleted,
            )

    def test_repair_migrates_only_proven_owned_entries(self):
        old_user = '"C:/Temp/Arvectum Proxy Launcher.exe" --start'
        old_recovery = '"C:/Legacy/Arvectum Proxy Launcher.exe" --start'
        fake = _FakeWinreg(
            {
                core._USER_AUTOSTART_RUN_VALUE: old_user,
                core._RECOVERY_RUN_VALUE: old_recovery,
            }
        )
        expected = '"C:/Documents/Arvectum Proxy Launcher.exe" --start'
        with mock.patch.object(core, "is_windows", return_value=True), \
             mock.patch.object(core, "managed_executable", return_value="C:/Documents/Arvectum Proxy Launcher.exe"), \
             mock.patch.object(core, "_is_proven_legacy_arvectum_start", return_value=True), \
             mock.patch.dict(sys.modules, {"winreg": fake}), \
             mock.patch.object(core, "_log"):
            self.assertTrue(recovery_autostart.repair_portable_run_entries())
        self.assertEqual(fake.values[core._USER_AUTOSTART_RUN_VALUE], expected)
        self.assertNotIn(core._RECOVERY_RUN_VALUE, fake.values)

        foreign_user = '"C:/Corporate/start.exe"'
        foreign_recovery = '"C:/Corporate/recover.exe"'
        fake = _FakeWinreg(
            {
                core._USER_AUTOSTART_RUN_VALUE: foreign_user,
                core._RECOVERY_RUN_VALUE: foreign_recovery,
            }
        )
        with mock.patch.object(core, "is_windows", return_value=True), \
             mock.patch.object(core, "managed_executable", return_value="C:/Documents/Arvectum Proxy Launcher.exe"), \
             mock.patch.object(core, "_is_proven_legacy_arvectum_start", return_value=False), \
             mock.patch.dict(sys.modules, {"winreg": fake}), \
             mock.patch.object(core, "_log"):
            self.assertTrue(recovery_autostart.repair_portable_run_entries())
        self.assertEqual(fake.values[core._USER_AUTOSTART_RUN_VALUE], foreign_user)
        self.assertEqual(fake.values[core._RECOVERY_RUN_VALUE], foreign_recovery)
        self.assertFalse(fake.set_calls)
        self.assertFalse(fake.delete_calls)

    def test_legacy_process_inspection_is_fail_closed_and_uses_core_seam(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / core._LAUNCHER_EXE_NAME
            target.write_bytes(b"x")
            command = '"%s" --start' % target
            with mock.patch.object(core, "is_windows", return_value=True), \
                 mock.patch.object(core.subprocess, "run", side_effect=RuntimeError("blocked")) as inspect, \
                 mock.patch.object(core, "_log"):
                self.assertTrue(recovery_autostart._recovery_legacy_process_active(command))
            inspect.assert_called_once()

    def test_missing_legacy_target_is_not_active(self):
        with mock.patch.object(core, "is_windows", return_value=True):
            self.assertFalse(
                recovery_autostart._recovery_legacy_process_active(
                    '"C:/Definitely/Missing/Arvectum Proxy Launcher.exe" --start'
                )
            )


if __name__ == "__main__":
    unittest.main()
