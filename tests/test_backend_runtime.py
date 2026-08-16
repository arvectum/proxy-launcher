import unittest

import backend_runtime
from linux_backend import LinuxBackend
from macos_backend import MacOSBackend
from windows_backend import WindowsBackend


class BackendRuntimeSelectionTests(unittest.TestCase):
    def test_windows_platform_selects_windows_backend(self):
        marker = object()
        backend = backend_runtime.create_backend("win32", legacy_core=marker)
        self.assertIsInstance(backend, WindowsBackend)
        self.assertEqual(backend.backend_id, "windows")
        self.assertIs(backend._core, marker)

    def test_macos_platform_selects_macos_backend(self):
        backend = backend_runtime.create_backend("darwin")
        self.assertIsInstance(backend, MacOSBackend)
        self.assertEqual(backend.backend_id, "macos")

    def test_linux_and_astra_python_platform_select_linux_backend(self):
        for platform in ("linux", "linux2"):
            with self.subTest(platform=platform):
                backend = backend_runtime.create_backend(platform)
                self.assertIsInstance(backend, LinuxBackend)
                self.assertEqual(backend.backend_id, "linux")

    def test_windows_requires_explicit_captured_legacy_core(self):
        with self.assertRaises(RuntimeError):
            backend_runtime.create_backend("win32")

    def test_unknown_platform_fails_closed(self):
        with self.assertRaises(backend_runtime.UnsupportedPlatformError):
            backend_runtime.backend_id_for_platform("freebsd14")
        with self.assertRaises(backend_runtime.UnsupportedPlatformError):
            backend_runtime.create_backend("freebsd14")


if __name__ == "__main__":
    unittest.main()
