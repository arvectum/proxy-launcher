"""Canonical system-proxy runtime composition for Arvectum Proxy Launcher.

This module owns platform backend selection and the public system-proxy seams.
The proven Windows proxy engine remains in ``proxy_core_legacy`` during the
behaviour-preserving APL-IP-003 migration; callers continue to import
``proxy_core`` while this module provides one explicit composition boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable

import backend_runtime
import linux_policykit_ux
from proxy_backend import ProxyBackendConfig


@dataclass(frozen=True)
class WindowsCoreAdapter:
    """Stable view of the captured Windows implementation before rewiring."""

    core: ModuleType
    enable: Callable[[], Any]
    disable: Callable[[], Any]
    enabled: Callable[[], Any]
    restore_pending: Callable[[], Any]
    sync_no_proxy: Callable[[], Any]

    def __getattr__(self, name: str) -> Any:
        return getattr(self.core, name)

    def enable_system_proxy(self):
        return self.enable()

    def disable_system_proxy(self):
        return self.disable()

    def system_proxy_enabled(self):
        return self.enabled()

    def network_restore_pending(self):
        return self.restore_pending()

    def sync_client_no_proxy(self):
        return self.sync_no_proxy()


class SystemProxyRuntime:
    """Own backend selection, capability gates and fail-closed dispatch."""

    def __init__(self, core: ModuleType, runtime_platform: Callable[[], str]):
        self.core = core
        self.runtime_platform = runtime_platform
        self._selected_backend = None
        self.windows_core = WindowsCoreAdapter(
            core=core,
            enable=core.enable_system_proxy,
            disable=core.disable_system_proxy,
            enabled=core.system_proxy_enabled,
            restore_pending=core.network_restore_pending,
            sync_no_proxy=core.sync_client_no_proxy,
        )

    def effective_platform(self) -> str:
        """Return production platform while preserving the historic Windows test seam."""
        try:
            if self.core.is_windows():
                return "win32"
        except Exception:
            pass
        return self.runtime_platform()

    def resolved_backend_config(self, settings=None) -> ProxyBackendConfig:
        settings = settings if settings is not None else self.core.load_settings()
        normalized = []
        seen = set()
        values = list(getattr(self.core, "DEFAULT_NO_PROXY", ())) + list(self.core.load_no_proxy())
        for raw in values:
            value = str(raw or "").strip().lower()
            if not value or value in seen:
                continue
            seen.add(value)
            normalized.append(value)
        return ProxyBackendConfig(
            pac_url=str(self.core.pac_url(settings)),
            http_proxy_url="http://127.0.0.1:%d" % int(settings.get("local_http_port", 8080)),
            no_proxy=tuple(normalized),
        )

    def backend_operational_status(self):
        return backend_runtime.operational_status_for_platform(self.effective_platform())

    def backend_operational_view(self):
        return backend_runtime.operational_status_view(self.backend_operational_status())

    def interactive_policykit_context(self) -> bool:
        return linux_policykit_ux.policykit_interaction_requested(self.effective_platform())

    def get_proxy_backend(self):
        if self._selected_backend is None:
            linux_runner = None
            if self.interactive_policykit_context():
                linux_runner = linux_policykit_ux.run_nmcli_with_policykit
            self._selected_backend = backend_runtime.create_backend(
                platform=self.effective_platform(),
                legacy_core=self.windows_core,
                logger=self.core._log,
                linux_runner=linux_runner,
            )
            self.core._log("system proxy backend selected: %s" % self._selected_backend.backend_id)
        return self._selected_backend

    def reset_for_tests(self) -> None:
        self._selected_backend = None

    def _backend_failure(self, operation: str, error: Exception) -> None:
        try:
            self.core._log("system proxy backend %s failed: %r" % (operation, error))
        except Exception:
            pass

    def require_new_mutation_operational(self):
        """Guard enable/reconfiguration; disable and recovery are never gated here."""
        platform = self.effective_platform()
        if not self.interactive_policykit_context():
            return backend_runtime.require_enable_operational(platform)

        status = backend_runtime.operational_status_for_platform(platform)
        if status.can_enable:
            return status
        if (
            str(platform).lower().startswith("linux")
            and status.state == backend_runtime.OperationalState.AUTH_REQUIRED
        ):
            return status
        raise backend_runtime.BackendOperationalError(status)

    def enable_system_proxy(self) -> bool:
        try:
            self.require_new_mutation_operational()
            return bool(self.get_proxy_backend().enable(self.resolved_backend_config()))
        except Exception as error:
            self._backend_failure("enable", error)
            return False

    def disable_system_proxy(self) -> bool:
        try:
            # Rollback must remain reachable even if readiness later degrades.
            return bool(self.get_proxy_backend().disable())
        except Exception as error:
            self._backend_failure("disable", error)
            return False

    def system_proxy_enabled(self) -> bool:
        try:
            return bool(self.get_proxy_backend().is_enabled(self.resolved_backend_config()))
        except Exception as error:
            self._backend_failure("status", error)
            return False

    def network_restore_pending(self) -> bool:
        try:
            return bool(self.get_proxy_backend().restore_pending())
        except Exception as error:
            self._backend_failure("restore-pending", error)
            return True

    def sync_client_no_proxy(self) -> bool:
        try:
            self.require_new_mutation_operational()
            return bool(self.get_proxy_backend().sync_no_proxy(self.resolved_backend_config()))
        except Exception as error:
            self._backend_failure("sync-no-proxy", error)
            return False

    def install_into_core(self) -> ModuleType:
        """Expose canonical runtime seams through the established module object."""
        self.core.resolved_backend_config = self.resolved_backend_config
        self.core.backend_operational_status = self.backend_operational_status
        self.core.backend_operational_view = self.backend_operational_view
        self.core.get_proxy_backend = self.get_proxy_backend
        self.core._reset_proxy_backend_for_tests = self.reset_for_tests
        self.core._interactive_policykit_context = self.interactive_policykit_context
        self.core._require_new_mutation_operational = self.require_new_mutation_operational
        self.core.enable_system_proxy = self.enable_system_proxy
        self.core.disable_system_proxy = self.disable_system_proxy
        self.core.system_proxy_enabled = self.system_proxy_enabled
        self.core.network_restore_pending = self.network_restore_pending
        self.core.sync_client_no_proxy = self.sync_client_no_proxy
        return self.core
