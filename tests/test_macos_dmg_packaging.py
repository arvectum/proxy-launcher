import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "tools" / "build_macos_dmg.sh").read_text(encoding="utf-8")

class MacOSDmgPackagingContractTests(unittest.TestCase):
    def test_uses_native_hdiutil_and_applications_link(self):
        self.assertIn('/usr/bin/hdiutil create', SCRIPT)
        self.assertIn('ln -s /Applications', SCRIPT)
        self.assertIn('hdiutil verify', SCRIPT)
    def test_dmg_build_cannot_mutate_proxy(self):
        for token in ('networksetup', 'sudo ', 'launchctl'):
            self.assertNotIn(token, SCRIPT)
    def test_version_and_arch_are_in_artifact_identity(self):
        self.assertIn('VERSION', SCRIPT)
        self.assertIn('uname -m', SCRIPT)
        self.assertIn('.dmg', SCRIPT)

if __name__ == '__main__': unittest.main()
