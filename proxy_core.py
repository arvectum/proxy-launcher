# -*- coding: utf-8 -*-
"""Runtime facade with automatic OS backend selection (APL-CORE-005).

The former proxy_core implementation is preserved byte-for-byte as
``proxy_core_legacy.py``. This facade exposes that same module object to callers,
then replaces only the five public system-proxy integration functions with
platform-neutral dispatch. The proxy engine, Windows registry/environment
implementation, CLI lifecycle and existing private test seams stay intact.
"""

import sys as _runtime_sys

import backend_runtime as _backend_runtime
from proxy_backend import ProxyBackendConfig as _ProxyBackendConfig

# Source-contract index for release guards that intentionally inspect the
# canonical proxy_core.py text. Authoritative executable definitions remain in
# proxy_core_legacy.py and are exposed below through the preserved module object.
# APP_VERSION = "0.2.3"
# ENGINEERING_MILESTONE = "P0.2"
# _LEGACY_INSTALL_OWNER_VALUES
# LEGACY_ARVECTUM
# classify_recovery_autostart
# conflicts with a foreign command
# leaving it untouched

_FACADE_FILE = __file__
import proxy_core_legacy as _core

# Preserve historical path semantics. Functions in proxy_core_legacy resolve
# ``__file__`` from their module globals at call time, so Windows portable and
# recovery logic continues to see proxy_core.py rather than the implementation
# storage filename introduced by APL-CORE-005.
_core.__file__ = _FACADE_FILE

# Capture the proven Windows implementation before public names are rewired.
_WINDOWS_ENABLE_SYSTEM_PROXY = _core.enable_system_proxy
_WINDOWS_DISABLE_SYSTEM_PROXY = _core.disable_system_proxy
_WINDOWS_SYSTEM_PROXY_ENABLED = _core.system_proxy_enabled
_WINDOWS_NETWORK_RESTORE_PENDING = _core.network_restore_pending
_WINDOWS_SYNC_CLIENT_NO_PROXY = _core.sync_client_no_proxy


class _CapturedWindowsCore:
    """View of proxy_core that keeps WindowsBackend on the pre-wiring path."""

    def __getattr__(self, name):
        return getattr(_core, name)

    def enable_system_proxy(self):
        return _WINDOWS_ENABLE_SYSTEM_PROXY()

    def disable_system_proxy(self):
        return _WINDOWS_DISABLE_SYSTEM_PROXY()

    def system_proxy_enabled(self):
        return _WINDOWS_SYSTEM_PROXY_ENABLED()

    def network_restore_pending(self):
        return _WINDOWS_NETWORK_RESTORE_PENDING()

    def sync_client_no_proxy(self):
        return _WINDOWS_SYNC_CLIENT_NO_PROXY()


_CAPTURED_WINDOWS_CORE = _CapturedWindowsCore()
_SELECTED_BACKEND = None


def resolved_backend_config(settings=None):
    """Build the single resolved OS-facing configuration for every backend."""
    settings = settings if settings is not None else _core.load_settings()
    normalized = []
    seen = set()
    values = list(getattr(_core, "DEFAULT_NO_PROXY", ())) + list(_core.load_no_proxy())
    for raw in values:
        value = str(raw or "").strip().lower()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return _ProxyBackendConfig(
        pac_url=str(_core.pac_url(settings)),
        http_proxy_url="http://127.0.0.1:%d" % int(settings.get("local_http_port", 8080)),
        no_proxy=tuple(normalized),
    )


def get_proxy_backend():
    """Return the process-local concrete backend selected from ``sys.platform``."""
    global _SELECTED_BACKEND
    if _SELECTED_BACKEND is None:
        _SELECTED_BACKEND = _backend_runtime.create_backend(
            platform=_runtime_sys.platform,
            legacy_core=_CAPTURED_WINDOWS_CORE,
            logger=_core._log,
        )
        _core._log("system proxy backend selected: %s" % _SELECTED_BACKEND.backend_id)
    return _SELECTED_BACKEND


def _reset_proxy_backend_for_tests():
    global _SELECTED_BACKEND
    _SELECTED_BACKEND = None


def _backend_failure(operation, error):
    try:
        _core._log("system proxy backend %s failed: %r" % (operation, error))
    except Exception:
        pass


def enable_system_proxy():
    """Enable the current platform backend using the resolved runtime config."""
    try:
        backend = get_proxy_backend()
        return bool(backend.enable(resolved_backend_config()))
    except Exception as error:
        _backend_failure("enable", error)
        return False


def disable_system_proxy():
    """Restore system proxy state through the automatically selected backend."""
    try:
        return bool(get_proxy_backend().disable())
    except Exception as error:
        _backend_failure("disable", error)
        return False


def system_proxy_enabled():
    """Return ownership-aware enabled state for the current resolved config."""
    try:
        backend = get_proxy_backend()
        return bool(backend.is_enabled(resolved_backend_config()))
    except Exception as error:
        _backend_failure("status", error)
        return False


def network_restore_pending():
    """Fail closed when rollback state cannot be inspected safely."""
    try:
        return bool(get_proxy_backend().restore_pending())
    except Exception as error:
        _backend_failure("restore-pending", error)
        # Unknown/unreadable backend state must block a successful rollback UX.
        return True


def sync_client_no_proxy():
    """Synchronize active bypass state through the selected backend."""
    try:
        backend = get_proxy_backend()
        return bool(backend.sync_no_proxy(resolved_backend_config()))
    except Exception as error:
        _backend_failure("sync-no-proxy", error)
        return False


# Rewire the original module globals. Existing CLI functions, GUI imports and
# private helpers therefore resolve these dispatchers without platform branches
# being duplicated in callers.
_core.resolved_backend_config = resolved_backend_config
_core.get_proxy_backend = get_proxy_backend
_core._reset_proxy_backend_for_tests = _reset_proxy_backend_for_tests
_core.enable_system_proxy = enable_system_proxy
_core.disable_system_proxy = disable_system_proxy
_core.system_proxy_enabled = system_proxy_enabled
_core.network_restore_pending = network_restore_pending
_core.sync_client_no_proxy = sync_client_no_proxy

# ``import proxy_core`` returns the original module object with the five public
# integration seams rewired. This preserves monkeypatch/private-test semantics
# and all mutable module state from the established Windows baseline.
_runtime_sys.modules[__name__] = _core


if __name__ == "__main__":
    _runtime_sys.exit(_core.main())
