import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "tools" / "build_macos_app.sh").read_text(encoding="utf-8")

class MacOSAppPackagingContractTests(unittest.TestCase):
    def test_app_identity_is_stable(self):
        self.assertIn('Arvectum Proxy Launcher.app', SCRIPT)
        self.assertIn('ru.arvectum.proxylauncher', SCRIPT)
        self.assertIn('--windowed', SCRIPT)
        self.assertIn('--onedir', SCRIPT)
    def test_app_build_has_no_network_or_proxy_mutation(self):
        for token in ('networksetup -set', 'sudo ', 'pkexec', 'curl '):
            self.assertNotIn(token, SCRIPT)
    def test_canonical_assets_are_bundled(self):
        self.assertIn('assets/arvectum.icns', SCRIPT)
        self.assertIn('no_proxy.txt:.', SCRIPT)
        self.assertIn('assets:assets', SCRIPT)

if __name__ == '__main__': unittest.main()
