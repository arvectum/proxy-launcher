import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT = (ROOT / "docs" / "APL_IP_002_LNX_LINUX_STACK_DEPENDENCY_SOVEREIGNTY_AUDIT.md").read_text(encoding="utf-8")
LOCK = (ROOT / "tools" / "appimage-toolchain.lock").read_text(encoding="utf-8")

class LinuxSovereigntyAuditContractTests(unittest.TestCase):
    def test_known_runtime_dependencies_are_audited(self):
        for dependency in ("NetworkManager", "nmcli", "PolicyKit", "Tcl/Tk", "os-release", "XDG"):
            self.assertIn(dependency, AUDIT)

    def test_known_build_dependencies_are_audited(self):
        for dependency in ("PyInstaller 6.22.0", "dpkg-deb", "appimagetool 1.9.1", "GitHub-hosted Ubuntu runners"):
            self.assertIn(dependency, AUDIT)

    def test_appimage_digest_controls_exist(self):
        self.assertRegex(LOCK, r"APPIMAGETOOL_SHA256=[0-9a-f]{64}")
        self.assertRegex(LOCK, r"APPIMAGE_RUNTIME_SHA256=[0-9a-f]{64}")

    def test_audit_does_not_claim_unconditional_sovereignty(self):
        self.assertIn("CONDITIONAL PASS", AUDIT)
        self.assertIn("P1 build sovereignty", AUDIT)
        self.assertIn("APL-LNX-010", AUDIT)

if __name__ == "__main__":
    unittest.main()
