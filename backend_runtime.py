# -*- coding: utf-8 -*-
"""Automatic operating-system backend selection for Arvectum Proxy Launcher.

APL-CORE-005 keeps platform detection in one small composition layer. Concrete
backends remain independently testable and are imported only for the selected
platform.
"""

import sys


class UnsupportedPlatformError(RuntimeError):
    """Raised when no governed system-proxy backend exists for this platform."""


def backend_id_for_platform(platform=None):
    """Return the stable backend id for a Python ``sys.platform`` value."""
    value = str(sys.platform if platform is None else platform).strip().lower()
    if value.startswith("win"):
        return "windows"
    if value == "darwin":
        return "macos"
    if value.startswith("linux"):
        return "linux"
    raise UnsupportedPlatformError(
        "unsupported operating system for system proxy backend: %s" % (value or "<empty>")
    )


def create_backend(platform=None, legacy_core=None, logger=None):
    """Instantiate the concrete backend selected for *platform*.

    Windows deliberately receives the captured legacy implementation from the
    runtime facade. This prevents the Windows adapter from recursively calling
    the new public dispatch functions while preserving the customer-proven
    Windows 0.2.3 mutation path byte-for-byte.
    """
    backend_id = backend_id_for_platform(platform)
    if backend_id == "windows":
        if legacy_core is None:
            raise RuntimeError(
                "Windows backend selection requires the captured legacy core adapter"
            )
        from windows_backend import WindowsBackend
        return WindowsBackend(legacy_core=legacy_core)
    if backend_id == "macos":
        from macos_backend import MacOSBackend
        return MacOSBackend(logger=logger)
    if backend_id == "linux":
        from linux_backend import LinuxBackend
        return LinuxBackend(logger=logger)
    raise AssertionError("unreachable backend id: %s" % backend_id)
