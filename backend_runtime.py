# -*- coding: utf-8 -*-
"""Automatic operating-system backend selection for Arvectum Proxy Launcher.

APL-CORE-005 keeps platform detection in one small composition layer. Concrete
backends remain independently testable and are imported only for the selected
platform.

APL-CORE-006 binds the selected backend to one explicit capability model so UI
and callers do not infer feature support independently from ``sys.platform``.
"""

import sys

from capability_model import capabilities_for_backend


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


def capabilities_for_platform(platform=None):
    """Return the declared product capabilities for the selected platform."""
    return capabilities_for_backend(backend_id_for_platform(platform))


def create_backend(platform=None, legacy_core=None, logger=None):
    """Instantiate the concrete backend selected for *platform*.

    Windows deliberately receives the captured legacy implementation from the
    runtime facade. This prevents the Windows adapter from recursively calling
    the new public dispatch functions while preserving the customer-proven
    Windows 0.2.3 mutation path byte-for-byte.
    """
    backend_id = backend_id_for_platform(platform)
    # Fail closed if a governed backend somehow exists without a capability
    # declaration. Selection and product UX must evolve as one reviewed unit.
    capabilities_for_backend(backend_id)
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
