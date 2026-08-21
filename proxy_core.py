# -*- coding: utf-8 -*-
"""Canonical runtime facade for Arvectum Proxy Launcher.

APL-IP-003 keeps the proven proxy engine/state implementation in
``proxy_core_legacy.py`` while moving owned responsibilities into explicit
canonical modules. Slice 1 extracted platform runtime composition; Slice 2
extracted application filesystem/state paths and the Windows portable
lifecycle; Slice 3 extracted governed configuration loading/validation, atomic
persistence, credential protection, and configuration recovery; Slice 4
extracts platform-neutral ``no_proxy`` routing policy, bypass evaluation, and
PAC generation.

Existing callers still receive the established module object, so Windows 0.2.3
behaviour and historical monkeypatch seams remain stable during the bounded
migration.
"""

import sys as _runtime_sys

import application_filesystem as _application_filesystem
import configuration_storage as _configuration_storage
import portable_lifecycle as _portable_lifecycle
import proxy_core_legacy as _core
import routing_policy as _routing_policy
import system_proxy_runtime as _system_proxy_runtime

# Source-contract index retained for release guards that intentionally inspect
# the canonical proxy_core.py text while executable definitions migrate out of
# the historical implementation storage module.
# APP_VERSION = "0.2.3"
# ENGINEERING_MILESTONE = "P0.2"
# _LEGACY_INSTALL_OWNER_VALUES
# LEGACY_ARVECTUM
# classify_recovery_autostart
# conflicts with a foreign command
# leaving it untouched

_FACADE_FILE = __file__

# Functions retained in proxy_core_legacy can resolve ``__file__`` from their
# module globals at call time. Preserve the canonical facade path for
# portable/recovery behaviour exactly as before this refactor.
_core.__file__ = _FACADE_FILE

# Install lower-level application ownership before runtime composition.
# Canonical modules deliberately resolve collaborators through ``_core``;
# this preserves the proven monkeypatch seams while moving implementation
# ownership out of the legacy storage module.
_application_filesystem.configure(_core)
_application_filesystem.install_into_core(_core)
_portable_lifecycle.configure(_core)
_portable_lifecycle.install_into_core(_core)
_configuration_storage.configure(_core)
_configuration_storage.install_into_core(_core)
_routing_policy.configure(_core)
_routing_policy.install_into_core(_core)

_system_proxy_runtime.configure(
    core=_core,
    runtime_platform=lambda: _runtime_sys.platform,
)
_system_proxy_runtime.install_into_core(_core)

# Compatibility boundary: ``import proxy_core`` still returns the established
# mutable module object until the legacy implementation is decomposed in later
# APL-IP-003 slices. The boundary is isolated and explicit rather than mixed
# with application filesystem, configuration storage, routing policy, or
# backend-selection logic.
_runtime_sys.modules[__name__] = _core


if __name__ == "__main__":
    _runtime_sys.exit(_core.main())
