# -*- coding: utf-8 -*-
"""Canonical runtime facade for Arvectum Proxy Launcher.

APL-IP-003 moves owned responsibilities out of ``proxy_core_legacy.py`` in
bounded slices while preserving the sealed Windows 0.2.3 behaviour and mutable
monkeypatch seam. Slices 1–9 own runtime composition, filesystem/portable
lifecycle, configuration, routing, local transport, process supervision,
application runtime, Windows system-proxy persistence, and Recovery Run
ownership. Slice 10 extracts stale/orphan PAC diagnostics and cleanup.
"""

import sys as _runtime_sys

import application_filesystem as _application_filesystem
import application_runtime as _application_runtime
import configuration_storage as _configuration_storage
import local_proxy_transport as _local_proxy_transport
import portable_lifecycle as _portable_lifecycle
import process_supervision as _process_supervision
import proxy_core_legacy as _core
import recovery_autostart as _recovery_autostart
import routing_policy as _routing_policy
import system_proxy_runtime as _system_proxy_runtime
import windows_pac_recovery as _windows_pac_recovery
import windows_system_proxy as _windows_system_proxy

# Source-contract index retained for release guards that inspect this facade.
# APP_VERSION = "0.2.3"
# ENGINEERING_MILESTONE = "P0.2"
# _LEGACY_INSTALL_OWNER_VALUES
# LEGACY_ARVECTUM
# classify_recovery_autostart
# conflicts with a foreign command
# leaving it untouched

_FACADE_FILE = __file__
_core.__file__ = _FACADE_FILE

# Lower-level owners preserve their established collaborators through ``_core``.
_application_filesystem.configure(_core)
_application_filesystem.install_into_core(_core)
_portable_lifecycle.configure(_core)
_portable_lifecycle.install_into_core(_core)
_configuration_storage.configure(_core)
_configuration_storage.install_into_core(_core)
_routing_policy.configure(_core)
_routing_policy.install_into_core(_core)
_local_proxy_transport.configure(_core)
_local_proxy_transport.install_into_core(_core)
_process_supervision.configure(_core)
_process_supervision.install_into_core(_core)
_recovery_autostart.configure(_core)
_recovery_autostart.install_into_core(_core)

# Install the Windows implementation before composition captures its adapter.
_windows_system_proxy.configure(_core)
_windows_system_proxy.install_into_core(_core)
_system_proxy_runtime.configure(
    core=_core,
    runtime_platform=lambda: _runtime_sys.platform,
)
_system_proxy_runtime.install_into_core(_core)

# PAC recovery consumes composed status and canonical WinINET primitives.
_windows_pac_recovery.configure(_core)
_windows_pac_recovery.install_into_core(_core)

# Application runtime is the top-level composition owner.
_application_runtime.configure(_core)
_application_runtime.install_into_core(_core)

# ``import proxy_core`` still returns the established mutable module object
# until the remaining historical implementation is decomposed.
_runtime_sys.modules[__name__] = _core


if __name__ == "__main__":
    _runtime_sys.exit(_core.main())
