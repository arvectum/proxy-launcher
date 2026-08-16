import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
HASH_LOCK = (ROOT / 'requirements-build.windows-x64.hashes.txt').read_text(encoding='utf-8')
BASE_LOCK = (ROOT / 'tools' / 'python-windows-base.lock').read_text(encoding='utf-8')
BUILD = (ROOT / 'tools' / 'clean_build_windows.ps1').read_text(encoding='utf-8')
PREPARE = (ROOT / 'tools' / 'prepare_windows_wheelhouse.ps1').read_text(encoding='utf-8')
PREPARE_BASE = (ROOT / 'tools' / 'prepare_windows_cpython_base.ps1').read_text(encoding='utf-8')
INSTALL_BASE = (ROOT / 'tools' / 'install_verified_windows_cpython.ps1').read_text(encoding='utf-8')


class WindowsOfflineBuildContractTests(unittest.TestCase):
    def test_hash_lock_contains_exact_eight_wheels(self):
        requirements = re.findall(r'^([A-Za-z0-9_.-]+)==([^\s\\]+)', HASH_LOCK, re.MULTILINE)
        hashes = re.findall(r'--hash=sha256:([0-9a-f]{64})', HASH_LOCK)
        self.assertEqual(len(requirements), 8)
        self.assertEqual(len(hashes), 8)
        self.assertEqual(len(set(hashes)), 8)
        self.assertIn(('pip', '26.1.2'), requirements)
        self.assertIn(('pyinstaller', '6.22.0'), requirements)

    def test_canonical_build_has_real_offline_hash_mode(self):
        for token in (
            'WheelhousePath', '--no-index', '--find-links', '--only-binary=:all:',
            '--require-hashes', 'offline-hash-locked',
            'requirements-build.windows-x64.hashes.txt',
        ):
            self.assertIn(token, BUILD)

    def test_online_build_uses_non_vulnerable_pinned_pip(self):
        self.assertIn('pip==26.1.2', BUILD)
        self.assertNotIn('pip==25.3', BUILD)

    def test_wheelhouse_acquisition_is_hash_verified_and_binary_only(self):
        for token in ('pip download', '--only-binary=:all:', '--no-deps', '--require-hashes'):
            self.assertIn(token, PREPARE)
        self.assertIn('Expected exactly 8 approved wheels', PREPARE)
        self.assertIn('wheelhouse-manifest.json', PREPARE)

    def test_cpython_base_identity_is_locked(self):
        for token in (
            'PYTHON_VERSION=3.12.10',
            'PYTHON_ARCH=x64',
            'python-3.12.10-amd64.exe',
            'PYTHON_INSTALLER_SIZE=26964224',
            'PYTHON_SIGSTORE_CERT_IDENTITY=thomas@python.org',
            'PYTHON_SIGSTORE_OIDC_ISSUER=https://accounts.google.com',
            'SIGSTORE_VERIFIER_VERSION=4.4.0',
        ):
            self.assertIn(token, BASE_LOCK)

    def test_cpython_acquisition_verifies_sigstore_identity(self):
        for token in (
            'python-windows-base.lock', 'sigstore verify identity', '--cert-identity',
            '--cert-oidc-issuer', '--bundle', 'sigstore-identity-pass',
            'cpython-base-manifest.json',
        ):
            self.assertIn(token, PREPARE_BASE)

    def test_verified_cpython_install_rechecks_hash_and_stays_isolated(self):
        for token in (
            'installer_sha256', 'Get-FileHash', 'TargetDir=', 'InstallAllUsers=0',
            'Include_launcher=0', 'PrependPath=0', 'AppendPath=0',
            'Include_pip=1', 'Include_tcltk=1',
        ):
            self.assertIn(token, INSTALL_BASE)

    def test_final_manifest_records_dependency_evidence(self):
        for token in ('dependency_mode', 'hash_lock_sha256', 'wheelhouse_manifest_sha256'):
            self.assertIn(token, BUILD)


if __name__ == '__main__':
    unittest.main()
