import json
import os
import tempfile
import unittest
import zipfile
from types import SimpleNamespace

from macos_diagnostics import collect_macos_diagnostics, write_macos_support_bundle
from macos_networksetup_preflight import MacOSPreflightStatus

class MacOSDiagnosticsTests(unittest.TestCase):
    def test_report_is_bounded_and_does_not_collect_secret_sources(self):
        runtime = SimpleNamespace(product_version="15.6", architecture="arm64", networksetup_path="/usr/sbin/networksetup", launchctl_path="/bin/launchctl", hdiutil_path="/usr/bin/hdiutil")
        preflight = SimpleNamespace(status=MacOSPreflightStatus.READY, enabled_services=("Wi-Fi",), readable_services=("Wi-Fi",), reasons=())
        report = collect_macos_diagnostics(runtime=runtime, preflight=preflight, command_runner=lambda args:{"returncode":0,"stdout":"ok","stderr":""})
        text = json.dumps(report).lower()
        self.assertIn("proxy credentials", text)
        self.assertNotIn("macos_proxy_backup.json", text)
        self.assertNotIn("os.environ", text)

    def test_zip_contains_only_governed_files(self):
        with tempfile.TemporaryDirectory() as temp:
            path = write_macos_support_bundle(os.path.join(temp, "support.zip"), report={"schema_version":1,"privacy":{"excluded":["credentials"]}})
            with zipfile.ZipFile(path) as archive:
                self.assertEqual(sorted(archive.namelist()), ["README.txt", "diagnostics.json"])

if __name__ == "__main__": unittest.main()
