import base64
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import windows_diagnostics as diag
from tests.test_windows_diagnostics import FakeCore


class SupportBundlePrivacyTests(unittest.TestCase):
    """APL-DIAG-006: treat the generated ZIP as an untrusted support artifact."""

    def _build_bundle(self, td, *, log_text="", env=None, mutate_fake=None):
        fake = FakeCore(td, windows=True)
        Path(fake.log_path()).write_text(log_text, encoding="utf-8")
        if mutate_fake is not None:
            mutate_fake(fake)
        output = Path(td) / "out" / "support.zip"
        with patch.object(diag, "core", fake), patch.dict(os.environ, env or {}, clear=True), patch.object(
            diag, "_collect_network_interfaces", return_value={"source": "test", "interfaces": []}
        ):
            result = Path(diag.create_support_bundle(str(output)))
        return fake, result

    @staticmethod
    def _read_members(bundle):
        with zipfile.ZipFile(bundle, "r") as archive:
            return {name: archive.read(name) for name in archive.namelist()}

    def test_bundle_member_allowlist_excludes_raw_state_files_and_temporary_files(self):
        with tempfile.TemporaryDirectory() as td:
            fake = FakeCore(td, windows=True)
            Path(fake.settings_path()).write_text('{"password":"raw-settings-file-secret"}', encoding="utf-8")
            Path(fake._internet_backup_path()).write_text(
                '{"ProxyServer":"http://u:raw-internet-backup-secret@proxy:1"}', encoding="utf-8"
            )
            Path(fake._env_backup_path()).write_text(
                '{"HTTP_PROXY":"http://u:raw-env-backup-secret@proxy:1"}', encoding="utf-8"
            )
            Path(fake.root / "unrelated-private.txt").write_text("unrelated-private-secret", encoding="utf-8")
            output = Path(td) / "out" / "support.zip"
            with patch.object(diag, "core", fake), patch.dict(os.environ, {}, clear=True), patch.object(
                diag, "_collect_network_interfaces", return_value={"source": "test", "interfaces": []}
            ):
                diag.create_support_bundle(str(output))

            members = self._read_members(output)
            self.assertEqual(set(members), {"diagnostics.json", "logs/proxy_core.log"})
            joined = b"\n".join(members.values()).decode("utf-8", errors="replace")
            for marker in (
                "raw-settings-file-secret",
                "raw-internet-backup-secret",
                "raw-env-backup-secret",
                "unrelated-private-secret",
            ):
                self.assertNotIn(marker, joined)
            self.assertFalse(any(output.parent.glob("*.tmp-*")))

    def test_bundle_redacts_credentials_across_settings_registry_environment_and_recovery(self):
        markers = {
            "settings": "APL006-settings-canary-7Yw3Jp",
            "wininet": "APL006-wininet-canary-2Qv8Km",
            "user_env": "APL006-userenv-canary-4Nd9Xs",
            "process_env": "APL006-processenv-canary-6Tr1Za",
            "recovery": "APL006-recovery-canary-8Bc5Lu",
        }

        def mutate(fake):
            original_load_settings = fake.load_settings

            def load_settings(migrate_legacy=True):
                value = original_load_settings(migrate_legacy=migrate_legacy)
                value["upstream"][0]["password"] = markers["settings"]
                return value

            fake.load_settings = load_settings
            fake._read_internet_settings = lambda: {
                "ProxyEnable": {"exists": True, "value": 1, "type": 4},
                "ProxyServer": {
                    "exists": True,
                    "value": "http://alice:%s@corp-proxy.example.test:3128" % markers["wininet"],
                    "type": 1,
                },
            }
            fake._read_user_env = lambda name: (
                (True, "http://bob:%s@user-proxy.example.test:8080" % markers["user_env"])
                if name == "HTTP_PROXY" else (False, "")
            )
            fake._get_recovery_run_value = lambda: (
                '"Arvectum Proxy Launcher.exe" --access-token %s --start' % markers["recovery"]
            )

        with tempfile.TemporaryDirectory() as td:
            _, bundle = self._build_bundle(
                td,
                env={"HTTP_PROXY": "http://carol:%s@process-proxy.example.test:9000" % markers["process_env"]},
                mutate_fake=mutate,
            )
            payload = b"\n".join(self._read_members(bundle).values()).decode("utf-8", errors="replace")

        for marker in markers.values():
            self.assertNotIn(marker, payload)
        self.assertIn("[REDACTED]", payload)
        self.assertIn("corp-proxy.example.test", payload)
        self.assertIn("process-proxy.example.test", payload)

    def test_bundle_redacts_secret_shapes_in_structured_and_plaintext_logs(self):
        # Assemble secret-shaped fixtures only at runtime. The repository must
        # not contain token/private-key lookalikes just to test the exporter.
        shape_provider = "g" + "hp_" + ("A" * 32)

        def b64url(value):
            raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
            return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

        shape_jwt = ".".join((b64url({"alg": "HS256"}), b64url({"sub": "apl-hidden-user"}), "sig" + ("X" * 32)))
        dash = chr(45) * 5
        shape_begin = dash + "BEGIN " + "PRIVATE KEY" + dash
        shape_end = dash + "END " + "PRIVATE KEY" + dash
        markers = (
            "APL006-log-password-3gV5mQ",
            "APL006-query-canary-9nK2wR",
            "APL006-header-canary-4pT7xL",
            shape_provider,
            shape_jwt,
            "APL006-pem-body-5Hs8Dc",
        )
        shape_pem = "\n".join((shape_begin, markers[5], shape_end))
        log_text = "\n".join((
            json.dumps({
                "schema": "arvectum.proxy.log.v1",
                "message": "request failed",
                "fields": {
                    "password": markers[0],
                    "url": "https://api.example.test/path?access_token=%s&mode=debug" % markers[1],
                },
            }),
            "X-API-Key: %s" % markers[2],
            "provider credential leaked as %s" % markers[3],
            "jwt credential leaked as %s" % markers[4],
            shape_pem,
        )) + "\n"

        with tempfile.TemporaryDirectory() as td:
            _, bundle = self._build_bundle(td, log_text=log_text)
            payload = self._read_members(bundle)["logs/proxy_core.log"].decode("utf-8", errors="replace")

        for marker in markers:
            self.assertNotIn(marker, payload)
        self.assertNotIn(shape_pem, payload)
        self.assertIn("[REDACTED]", payload)
        self.assertIn("api.example.test", payload)

    def test_exception_text_is_redacted_before_entering_diagnostics_json(self):
        marker = "APL006-exception-canary-6Mx2Qa"

        def broken():
            raise RuntimeError("failed with Authorization: Bearer %s and password=%s" % (marker, marker))

        with patch.object(diag, "_SECTION_COLLECTORS", (("broken", broken),)):
            snapshot = diag.collect_snapshot()

        encoded = json.dumps(snapshot, ensure_ascii=False)
        self.assertNotIn(marker, encoded)
        self.assertIn("[REDACTED]", encoded)
        self.assertFalse(snapshot["sections"]["broken"]["ok"])

    def test_zip_paths_are_relative_fixed_names_without_source_filesystem_leakage(self):
        with tempfile.TemporaryDirectory(prefix="APL006-private-user-path-") as td:
            _, bundle = self._build_bundle(td, log_text="hello\n")
            members = self._read_members(bundle)

        for name in members:
            self.assertFalse(name.startswith(("/", "\\")))
            self.assertNotIn("..", Path(name).parts)
            self.assertNotIn("APL006-private-user-path-", name)
            self.assertNotIn(":", name)

    def test_diagnostics_json_is_valid_for_clean_input(self):
        with tempfile.TemporaryDirectory() as td:
            fake = FakeCore(td, windows=True)
            fake.load_settings = lambda migrate_legacy=True: {
                "local_http_port": 8080,
                "local_socks_port": 1080,
                "local_pac_port": 8082,
                "pac_path": "/proxy.pac",
                "upstream": [{"host": "proxy.example.test", "port": 8000}],
            }
            fake._read_internet_settings = lambda: {}
            fake._read_user_env = lambda name: (False, "")
            fake._get_recovery_run_value = lambda: None
            output = Path(td) / "support.zip"
            with patch.object(diag, "core", fake), patch.dict(os.environ, {}, clear=True), patch.object(
                diag, "_collect_network_interfaces", return_value={"source": "test", "interfaces": []}
            ):
                diag.create_support_bundle(str(output))
            data = json.loads(self._read_members(output)["diagnostics.json"].decode("utf-8"))

        self.assertEqual(data["schema"], diag.SCHEMA)
        self.assertEqual(data["collector_version"], diag.COLLECTOR_VERSION)
        self.assertIn("sections", data)


if __name__ == "__main__":
    unittest.main()
