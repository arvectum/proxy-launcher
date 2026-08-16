import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = (ROOT / "tools" / "build_macos_app.sh").read_text(encoding="utf-8")
DMG = (ROOT / "tools" / "build_macos_dmg.sh").read_text(encoding="utf-8")
AUTOSTART = (ROOT / "macos_autostart.py").read_text(encoding="utf-8")
BACKEND = (ROOT / "macos_backend.py").read_text(encoding="utf-8")

class MacOSPackagingRecoveryContractTests(unittest.TestCase):
    def test_packaging_does_not_own_network_recovery(self):
        combined = APP + "\n" + DMG
        for token in ("macos_proxy_backup.json", "networksetup -set", "restore_pending", "Library/Application Support/Arvectum"):
            self.assertNotIn(token, combined)
        self.assertIn("macos_proxy_backup.json", BACKEND)
        self.assertIn("restore_pending", BACKEND)

    def test_autostart_is_separate_from_recovery_state(self):
        self.assertIn("Library", AUTOSTART)
        self.assertIn("LaunchAgents", AUTOSTART)
        self.assertNotIn("macos_proxy_backup.json", AUTOSTART)
        self.assertNotIn("networksetup", AUTOSTART)

    def test_dmg_has_no_install_or_remove_hooks(self):
        for token in ("postinstall", "preinstall", "uninstall", "pkgbuild", "installer -pkg"):
            self.assertNotIn(token, DMG)

if __name__ == '__main__': unittest.main()
