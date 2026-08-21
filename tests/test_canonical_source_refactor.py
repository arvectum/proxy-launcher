import json
import os
import pathlib
import tempfile
import unittest
from unittest import mock

import proxy_core as core


ROOT = pathlib.Path(__file__).resolve().parents[1]


class CanonicalSourceRefactorTests(unittest.TestCase):
    def test_mailmap_normalizes_only_human_historical_identities(self):
        text = (ROOT / ".mailmap").read_text(encoding="utf-8")
        self.assertIn("arvectum", text)
        self.assertIn("arutyunoveth", text)
        self.assertIn("Arvectum <arvectum@gmail.com>", text)
        for forbidden in ("OpenAI", "GitHub Actions", "noreply@openai.com"):
            self.assertNotIn(forbidden, text)

    def test_proxy_core_is_thin_composition_boundary(self):
        facade = (ROOT / "proxy_core.py").read_text(encoding="utf-8")
        runtime = (ROOT / "system_proxy_runtime.py").read_text(encoding="utf-8")
        filesystem = (ROOT / "application_filesystem.py").read_text(encoding="utf-8")
        configuration = (ROOT / "configuration_storage.py").read_text(encoding="utf-8")
        portable = (ROOT / "portable_lifecycle.py").read_text(encoding="utf-8")

        for module_name in (
            "application_filesystem",
            "configuration_storage",
            "portable_lifecycle",
            "system_proxy_runtime",
            "proxy_core_legacy",
        ):
            self.assertIn(module_name, facade)
        self.assertIn("sys.modules", facade.replace("_runtime_sys.modules", "sys.modules"))
        self.assertLess(len(facade), 5000)

        self.assertIn("class WindowsCoreAdapter", runtime)
        self.assertIn("def configure", runtime)
        self.assertIn("def install_into_core", runtime)
        self.assertIn("fail-closed", runtime.lower())

        for source in (filesystem, configuration, portable):
            self.assertIn("def configure", source)
            self.assertIn("def install_into_core", source)
        self.assertIn("def ensure_state_ready", filesystem)
        self.assertIn("def migration_error_path", filesystem)
        self.assertIn("def _validate_settings_model", configuration)
        self.assertIn("def _atomic_write_bytes", configuration)
        self.assertIn("def _recover_corrupt_settings", configuration)
        self.assertIn("def load_settings", configuration)
        self.assertIn("def save_settings", configuration)
        self.assertIn("def ensure_stable_app_copy", portable)
        self.assertIn("def handoff_to_stable_copy", portable)

    def test_slice2_runtime_functions_are_owned_by_canonical_modules(self):
        for name in (
            "install_dir",
            "data_dir",
            "ensure_state_ready",
            "settings_path",
            "pid_path",
            "log_path",
        ):
            self.assertEqual(getattr(core, name).__module__, "application_filesystem")
        for name in (
            "_sha256_file",
            "ensure_stable_app_copy",
            "managed_executable",
            "handoff_to_stable_copy",
            "canonical_install_exe",
        ):
            self.assertEqual(getattr(core, name).__module__, "portable_lifecycle")

    def test_slice3_configuration_functions_are_owned_by_canonical_module(self):
        for name in (
            "_validate_runtime_settings",
            "_validate_serialized_settings",
            "_disk_contains_plaintext_credentials",
            "_atomic_write_bytes",
            "_atomic_write_json",
            "_atomic_write_text",
            "_load_serialized_settings",
            "_runtime_settings_from_disk",
            "_quarantine_corrupt_file",
            "_record_configuration_recovery",
            "_recover_corrupt_settings",
            "_decode_upstream_secrets",
            "_encode_settings_for_disk",
            "load_settings",
            "save_settings",
        ):
            self.assertEqual(getattr(core, name).__module__, "configuration_storage")

    def test_slice3_no_proxy_keeps_atomic_writer_compatibility_seam(self):
        with mock.patch.object(core, "no_proxy_path", return_value="/tmp/apl-ip-003-no-proxy"), \
             mock.patch.object(core, "_atomic_write_text") as writer:
            self.assertTrue(core.save_no_proxy(["https://Example.COM/path", "example.com"]))
        self.assertTrue(writer.called)
        payload = writer.call_args.args[1]
        self.assertEqual(payload.count("example.com"), 1)

    def test_slice2_state_migration_preserves_monkeypatch_seams(self):
        with tempfile.TemporaryDirectory() as td:
            legacy = pathlib.Path(td) / "legacy"
            stable = pathlib.Path(td) / "stable"
            legacy.mkdir()
            (legacy / "proxy_settings.json").write_text(
                json.dumps(core.DEFAULT_SETTINGS), encoding="utf-8"
            )
            (legacy / "no_proxy.txt").write_text("example.invalid\n", encoding="utf-8")

            with mock.patch.object(core, "data_dir", return_value=str(stable)), \
                 mock.patch.object(core, "_legacy_state_dirs", return_value=[str(legacy)]), \
                 mock.patch.object(core, "_STATE_READY", False):
                self.assertTrue(core.ensure_state_ready())

            self.assertTrue((stable / "proxy_settings.json").is_file())
            self.assertEqual(
                (stable / "no_proxy.txt").read_text(encoding="utf-8"),
                "example.invalid\n",
            )

    def test_slice2_state_migration_path_resolution_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            stable = pathlib.Path(td) / "stable"
            legacy = pathlib.Path(td) / "legacy"
            with mock.patch.object(core, "data_dir", return_value=str(stable)), \
                 mock.patch.object(core, "_legacy_state_dirs", return_value=[str(legacy)]), \
                 mock.patch.object(core, "_STATE_READY", False), \
                 mock.patch.object(
                     core.os.path,
                     "realpath",
                     side_effect=OSError("path resolution failed"),
                 ):
                self.assertFalse(core.ensure_state_ready())

    def test_slice2_portable_self_heal_preserves_hash_guard(self):
        with tempfile.TemporaryDirectory() as td:
            source = pathlib.Path(td) / "Downloads" / "Arvectum Proxy Launcher.exe"
            target = (
                pathlib.Path(td)
                / "Documents"
                / "ArvectumProxyLauncher"
                / "Arvectum Proxy Launcher.exe"
            )
            source.parent.mkdir()
            target.parent.mkdir(parents=True)
            source.write_bytes(b"new portable payload")
            target.write_bytes(b"old payload")

            with mock.patch.object(core, "is_windows", return_value=True), \
                 mock.patch.object(core.sys, "frozen", True, create=True), \
                 mock.patch.object(core.sys, "executable", str(source)), \
                 mock.patch.object(core, "stable_app_exe", return_value=str(target)), \
                 mock.patch.object(core, "_log"):
                self.assertEqual(core.ensure_stable_app_copy(), os.path.realpath(target))
                self.assertEqual(core.canonical_install_exe(), os.path.realpath(target))

            self.assertEqual(target.read_bytes(), source.read_bytes())
            self.assertEqual(
                (target.parent / core._INSTALL_OWNER_MARKER).read_text(encoding="ascii"),
                core._INSTALL_OWNER_VALUE,
            )

    def test_runtime_preserves_recovery_without_enable_preflight(self):
        runtime = (ROOT / "system_proxy_runtime.py").read_text(encoding="utf-8")
        disable_body = runtime.split("\ndef disable_system_proxy", 1)[1].split("\ndef system_proxy_enabled", 1)[0]
        restore_body = runtime.split("\ndef network_restore_pending", 1)[1].split("\ndef sync_client_no_proxy", 1)[0]
        self.assertNotIn("require_new_mutation_operational", disable_body)
        self.assertNotIn("require_new_mutation_operational", restore_body)
        self.assertIn("return True", restore_body)

    def test_historical_customer_baseline_is_not_relabelled(self):
        baseline = (ROOT / "release" / "baselines" / "APL-CLIENT-002_WINDOWS_0.2.3_CUSTOMER_CONFIRMED.md").read_text(encoding="utf-8-sig")
        self.assertIn("CONFIRMED CUSTOMER BASELINE FROZEN", baseline)
        self.assertIn("0.2.3", baseline)


if __name__ == "__main__":
    unittest.main()
