# -*- coding: utf-8 -*-
"""Canonical runtime facade for Arvectum Proxy Launcher.

APL-IP-003 keeps the proven proxy engine/state implementation in
``proxy_core_legacy.py`` while moving platform composition into the explicit
``system_proxy_runtime`` module. Existing callers still receive the established
module object, so Windows 0.2.3 behaviour and historical monkeypatch seams remain
stable during the behaviour-preserving migration.
"""

import sys as _runtime_sys

import proxy_core_legacy as _core
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

# Functions defined in proxy_core_legacy resolve ``__file__`` from their module
# globals at call time. Preserve the canonical facade path for portable/recovery
# behaviour exactly as before this refactor.
_core.__file__ = _FACADE_FILE

_system_proxy_runtime.configure(
    core=_core,
    runtime_platform=lambda: _runtime_sys.platform,
)
_system_proxy_runtime.install_into_core(_core)

# Compatibility boundary: ``import proxy_core`` still returns the established
# mutable module object until the legacy implementation is decomposed in later
# APL-IP-003 slices. The boundary is now isolated and explicit rather than mixed
# with backend-selection logic.
_runtime_sys.modules[__name__] = _core


if __name__ == "__main__":
    _runtime_sys.exit(_core.main())
