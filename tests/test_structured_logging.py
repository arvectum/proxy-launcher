import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import proxy_core as core
from structured_logging import SCHEMA, StructuredLogger


class StructuredLoggerTests(unittest.TestCase):
    def test_core_log_emits_jsonl_schema_event_and_level(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "proxy_core.log"
            with mock.patch.object(core, "log_path", return_value=str(path)):
                core._log("proxy started (http=8080 socks=1080 pac=8082, upstreams=1)")
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertEqual(record["schema"], SCHEMA)
            self.assertEqual(record["event"], "proxy.started")
            self.assertEqual(record["level"], "INFO")
            self.assertEqual(record["app_version"], core.APP_VERSION)
            self.assertEqual(record["milestone"], core.ENGINEERING_MILESTONE)
            self.assertTrue(record["ts"].endswith("Z"))
            self.assertEqual(record["component"], "proxy_core")
            self.assertTrue(record["run_id"])

    def test_core_explicit_structured_log_accepts_fields_and_redacts_secrets(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "proxy_core.log"
            with mock.patch.object(core, "log_path", return_value=str(path)):
                core.structured_log(
                    "proxy=http://alice:hunter2@example.test password=hunter2 "
                    "Proxy-Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==",
                    event="diagnostics.redaction",
                    password="hunter2",
                    authorization="Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==",
                    nested={"token": "top-secret-token", "host": "example.test"},
                )
            raw = path.read_text(encoding="utf-8")
            for secret in ("hunter2", "QWxhZGRpbjpvcGVuIHNlc2FtZQ==", "top-secret-token"):
                self.assertNotIn(secret, raw)
            data = json.loads(raw)
            self.assertIn("example.test", raw)
            self.assertEqual(data["fields"]["password"], "[REDACTED]")
            self.assertEqual(data["fields"]["nested"]["token"], "[REDACTED]")

    def test_legacy_plaintext_log_is_preserved_separately(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "proxy_core.log"
            old = "2026-08-15 10:20:30 old plaintext diagnostic\n"
            path.write_text(old, encoding="utf-8")
            logger = StructuredLogger(lambda: str(path), "0.2.3", "P0.2")
            logger.log("settings saved")
            self.assertEqual(Path(str(path) + ".legacy").read_text(encoding="utf-8"), old)
            current = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(current), 1)
            self.assertEqual(json.loads(current[0])["schema"], SCHEMA)

    def test_rotation_is_bounded_and_all_records_remain_json(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "proxy_core.log"
            logger = StructuredLogger(lambda: str(path), "0.2.3", "P0.2", max_bytes=600, backups=2)
            for index in range(20):
                logger.log("diagnostic record %d %s" % (index, "x" * 120))
            self.assertTrue(path.exists())
            self.assertTrue(Path(str(path) + ".1").exists())
            self.assertFalse(Path(str(path) + ".3").exists())
            for candidate in (path, Path(str(path) + ".1"), Path(str(path) + ".2")):
                if not candidate.exists():
                    continue
                for line in candidate.read_text(encoding="utf-8").splitlines():
                    self.assertEqual(json.loads(line)["schema"], SCHEMA)

    def test_logging_failure_never_raises(self):
        logger = StructuredLogger(lambda: "\0invalid-log-path", "0.2.3", "P0.2")
        self.assertIsNone(logger.log("this must not crash the proxy"))

    def test_error_and_warning_inference(self):
        logger = StructuredLogger(lambda: os.devnull, "0.2.3", "P0.2")
        self.assertEqual(logger.make_record("settings save error: denied")["level"], "ERROR")
        self.assertEqual(logger.make_record("restore skipped: ownership unverified")["level"], "WARNING")

    def test_existing_log_mock_contract_is_unchanged(self):
        captured = []
        with mock.patch.object(core, "_log", side_effect=captured.append):
            core._log("system proxy restore skipped: ownership unverified")
        self.assertEqual(captured, ["system proxy restore skipped: ownership unverified"])


if __name__ == "__main__":
    unittest.main()
