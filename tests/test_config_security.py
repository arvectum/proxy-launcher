import json
import os
import tempfile
from pathlib import Path
import unittest
from unittest import mock

import configuration_storage
import proxy_core as core


class ConfigSecurityTests(unittest.TestCase):
    def test_configuration_model_is_versioned_and_rejects_unknown_keys(self):
        valid = core._validate_runtime_settings(core.DEFAULT_SETTINGS)
        self.assertEqual(valid["config_version"], core.CONFIG_VERSION)
        invalid = dict(core.DEFAULT_SETTINGS)
        invalid["surprise"] = True
        with self.assertRaises(ValueError):
            core._validate_runtime_settings(invalid)

    def test_configuration_model_rejects_invalid_or_colliding_ports(self):
        invalid = dict(core.DEFAULT_SETTINGS)
        invalid["local_http_port"] = 70000
        with self.assertRaises(ValueError):
            core._validate_runtime_settings(invalid)
        collision = dict(core.DEFAULT_SETTINGS)
        collision["local_socks_port"] = collision["local_http_port"]
        with self.assertRaises(ValueError):
            core._validate_runtime_settings(collision)

    def test_future_configuration_version_fails_closed(self):
        future = dict(core.DEFAULT_SETTINGS)
        future["config_version"] = core.CONFIG_VERSION + 1
        with self.assertRaises(ValueError):
            core._validate_runtime_settings(future)

    def test_config_security_paths_are_stable_under_data_dir(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(core, "data_dir", return_value=td):
            expected = os.path.realpath(td)
            for candidate in (
                core.settings_path(), core.settings_backup_path(), core.config_recovery_path(),
                core.config_quarantine_dir(), core.no_proxy_path(),
            ):
                self.assertEqual(os.path.commonpath([expected, os.path.realpath(candidate)]), expected)

    def test_windows_disk_secret_boundary_uses_only_dpapi_blob(self):
        settings = dict(core.DEFAULT_SETTINGS)
        settings["upstream"] = [{
            "host": "proxy.test", "port": 8000,
            "username": "alice", "password": "secret-value",
        }]
        with mock.patch.object(core, "is_windows", return_value=True), \
             mock.patch.object(core, "_dpapi_protect_text", return_value="ENCRYPTED"):
            disk = core._encode_settings_for_disk(settings)
        upstream = disk["upstream"][0]
        self.assertEqual(upstream["credentials_dpapi"], "ENCRYPTED")
        self.assertNotIn("username", upstream)
        self.assertNotIn("password", upstream)

    def test_legacy_windows_migration_never_creates_plaintext_lastgood(self):
        with tempfile.TemporaryDirectory() as td:
            primary = Path(td) / "proxy_settings.json"
            backup = Path(td) / "proxy_settings.lastgood.json"
            primary.write_text(json.dumps({
                "local_http_port": 8080,
                "local_socks_port": 1080,
                "local_pac_port": 8082,
                "pac_path": "/proxy.pac",
                "upstream": [{
                    "host": "proxy.test", "port": 8000,
                    "username": "legacy-user", "password": "legacy-secret",
                }],
            }), encoding="utf-8")
            with mock.patch.object(core, "data_dir", return_value=td), \
                 mock.patch.object(core, "is_windows", return_value=True), \
                 mock.patch.object(core, "_dpapi_protect_text", return_value="ENCRYPTED"):
                self.assertTrue(core.save_settings(core._runtime_settings_from_disk(
                    core._load_serialized_settings(str(primary)))))
            disk = json.loads(primary.read_text(encoding="utf-8"))
            self.assertFalse(backup.exists())
            self.assertNotIn("username", disk["upstream"][0])
            self.assertNotIn("password", disk["upstream"][0])
            self.assertEqual(disk["upstream"][0]["credentials_dpapi"], "ENCRYPTED")

    def test_read_only_load_does_not_quarantine_corruption(self):
        with tempfile.TemporaryDirectory() as td:
            primary = Path(td) / "proxy_settings.json"
            primary.write_text("{broken-json", encoding="utf-8")
            with mock.patch.object(core, "data_dir", return_value=td):
                loaded = core.load_settings(migrate_legacy=False)
            self.assertEqual(loaded, core.DEFAULT_SETTINGS)
            self.assertTrue(primary.exists())
            self.assertFalse((Path(td) / "quarantine").exists())

    def test_atomic_save_failure_preserves_previous_primary(self):
        with tempfile.TemporaryDirectory() as td:
            primary = Path(td) / "proxy_settings.json"
            previous = core._validate_serialized_settings({
                "local_http_port": 8080,
                "local_socks_port": 1080,
                "local_pac_port": 8082,
                "pac_path": "/proxy.pac",
                "upstream": [{"host": "old.proxy", "port": 8000}],
            })
            primary.write_text(json.dumps(previous), encoding="utf-8")
            before = primary.read_bytes()
            real_replace = os.replace

            def fail_primary(src, dst):
                if os.path.realpath(dst) == os.path.realpath(primary):
                    raise OSError("injected replace failure")
                return real_replace(src, dst)

            updated = dict(core.DEFAULT_SETTINGS)
            updated["upstream"] = [{
                "host": "new.proxy", "port": 9000, "username": "", "password": ""
            }]
            with mock.patch.object(core, "data_dir", return_value=td), \
                 mock.patch.object(configuration_storage.os, "replace", side_effect=fail_primary):
                self.assertFalse(core.save_settings(updated))
            self.assertEqual(primary.read_bytes(), before)

    def test_atomic_writer_flushes_with_fsync(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "value.json"
            with mock.patch.object(configuration_storage.os, "fsync", wraps=os.fsync) as fsync:
                core._atomic_write_json(str(target), {"ok": True})
            self.assertTrue(target.exists())
            self.assertGreaterEqual(fsync.call_count, 1)

    def test_no_proxy_uses_atomic_writer_and_normalizes_entries(self):
        with mock.patch.object(core, "no_proxy_path", return_value="/tmp/no-proxy-test"), \
             mock.patch.object(core, "_atomic_write_text") as write:
            self.assertTrue(core.save_no_proxy(["https://Example.COM/path", "example.com", "#ignore"]))
        payload = write.call_args.args[1]
        self.assertIn("example.com", payload)
        self.assertEqual(payload.count("example.com"), 1)

    def test_corrupt_primary_is_quarantined_and_lastgood_restored(self):
        with tempfile.TemporaryDirectory() as td:
            primary = Path(td) / "proxy_settings.json"
            backup = Path(td) / "proxy_settings.lastgood.json"
            primary.write_text("{broken-json", encoding="utf-8")
            lastgood = core._validate_serialized_settings({
                "local_http_port": 8181,
                "local_socks_port": 1181,
                "local_pac_port": 8182,
                "pac_path": "/proxy.pac",
                "upstream": [{"host": "good.proxy", "port": 8000}],
            })
            backup.write_text(json.dumps(lastgood), encoding="utf-8")
            with mock.patch.object(core, "data_dir", return_value=td), \
                 mock.patch.object(core, "is_windows", return_value=False):
                loaded = core.load_settings()
            self.assertEqual(loaded["local_http_port"], 8181)
            self.assertEqual(json.loads(primary.read_text(encoding="utf-8"))["local_http_port"], 8181)
            quarantined = list((Path(td) / "quarantine").glob("proxy_settings.json.corrupt-*"))
            self.assertTrue(quarantined)
            evidence = json.loads((Path(td) / "config_recovery.json").read_text(encoding="utf-8"))
            self.assertEqual(evidence["recovered_from"], "lastgood")

    def test_corrupt_primary_without_backup_falls_back_to_defaults_and_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            primary = Path(td) / "proxy_settings.json"
            primary.write_text("not-json", encoding="utf-8")
            with mock.patch.object(core, "data_dir", return_value=td):
                loaded = core.load_settings()
            self.assertEqual(loaded, core.DEFAULT_SETTINGS)
            self.assertFalse(primary.exists())
            self.assertTrue(list((Path(td) / "quarantine").glob("proxy_settings.json.corrupt-*")))
            evidence = json.loads((Path(td) / "config_recovery.json").read_text(encoding="utf-8"))
            self.assertEqual(evidence["recovered_from"], "programmatic_defaults")

    def test_corrupt_lastgood_is_quarantined_before_default_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            primary = Path(td) / "proxy_settings.json"
            backup = Path(td) / "proxy_settings.lastgood.json"
            primary.write_text("bad-primary", encoding="utf-8")
            backup.write_text("bad-backup", encoding="utf-8")
            with mock.patch.object(core, "data_dir", return_value=td):
                loaded = core.load_settings()
            self.assertEqual(loaded, core.DEFAULT_SETTINGS)
            qdir = Path(td) / "quarantine"
            self.assertTrue(list(qdir.glob("proxy_settings.json.corrupt-*")))
            self.assertTrue(list(qdir.glob("proxy_settings.lastgood.json.corrupt-*")))

    def test_io_error_is_not_misclassified_as_corruption(self):
        with tempfile.TemporaryDirectory() as td:
            primary = Path(td) / "proxy_settings.json"
            primary.write_text(json.dumps(core.DEFAULT_SETTINGS), encoding="utf-8")
            real_open = configuration_storage.io.open

            def denied(path, *args, **kwargs):
                if os.path.realpath(path) == os.path.realpath(primary):
                    raise PermissionError("locked")
                return real_open(path, *args, **kwargs)

            with mock.patch.object(core, "data_dir", return_value=td), \
                 mock.patch.object(configuration_storage.io, "open", side_effect=denied):
                loaded = core.load_settings()
            self.assertEqual(loaded, core.DEFAULT_SETTINGS)
            self.assertTrue(primary.exists())
            self.assertFalse((Path(td) / "quarantine").exists())


if __name__ == "__main__":
    unittest.main()
