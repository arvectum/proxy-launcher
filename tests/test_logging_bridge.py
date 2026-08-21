import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import proxy_core as core
from structured_logging import SCHEMA, StructuredLogger


class LoggingBridgeOwnershipTests(unittest.TestCase):
    def test_slice11_functions_are_owned_by_canonical_module(self):
        self.assertEqual(core.structured_log.__module__, "logging_bridge")
        self.assertEqual(core._log.__module__, "logging_bridge")

    def test_core_logger_singleton_preserves_exact_metadata_contract(self):
        self.assertIsInstance(core.structured_logger, StructuredLogger)
        self.assertEqual(core.structured_logger.app_version, core.APP_VERSION)
        self.assertEqual(core.structured_logger.milestone, core.ENGINEERING_MILESTONE)
        self.assertEqual(core.structured_logger.component, "proxy_core")
        self.assertTrue(core.structured_logger.run_id)

    def test_logger_path_getter_keeps_dynamic_core_monkeypatch_seam(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "proxy_core.log"
            with mock.patch.object(core, "log_path", return_value=str(path)):
                record = core._log("proxy started (http=8080 socks=1080 pac=8082, upstreams=1)")

            self.assertEqual(record["schema"], SCHEMA)
            self.assertEqual(record["event"], "proxy.started")
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["app_version"], core.APP_VERSION)
            self.assertEqual(payload["milestone"], core.ENGINEERING_MILESTONE)
            self.assertEqual(payload["component"], "proxy_core")

    def test_structured_log_resolves_mutable_logger_seam_at_call_time(self):
        fake_logger = mock.Mock()
        fake_logger.log.return_value = {"ok": True}
        with mock.patch.object(core, "structured_logger", fake_logger):
            result = core.structured_log(
                "diagnostic",
                level="WARNING",
                event="test.event",
                answer=42,
            )

        self.assertEqual(result, {"ok": True})
        fake_logger.log.assert_called_once_with(
            "diagnostic",
            level="WARNING",
            event="test.event",
            fields={"answer": 42},
        )

    def test_compatibility_log_resolves_mutable_structured_log_seam(self):
        sentinel = object()
        with mock.patch.object(core, "structured_log", return_value=sentinel) as structured:
            self.assertIs(core._log("compatibility message"), sentinel)
        structured.assert_called_once_with("compatibility message")

    def test_empty_fields_keep_historical_none_contract(self):
        fake_logger = mock.Mock()
        with mock.patch.object(core, "structured_logger", fake_logger):
            core.structured_log("diagnostic")
        fake_logger.log.assert_called_once_with(
            "diagnostic",
            level=None,
            event=None,
            fields=None,
        )

    def test_real_logger_io_failure_remains_never_raise(self):
        with mock.patch.object(core, "log_path", return_value="\0invalid-log-path"):
            self.assertIsNone(core.structured_log("logging failure must not break recovery"))


if __name__ == "__main__":
    unittest.main()
