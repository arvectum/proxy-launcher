# -*- coding: utf-8 -*-
"""Windows implementation of the ProxyBackend contract.

APL-CORE-002 is intentionally a compatibility extraction: the proven Windows
0.2.3 registry, environment and rollback implementation remains in
``proxy_core`` for now, while this class gives the application a concrete
platform backend with configuration-specific semantics.
"""

from typing import Any, Iterable, Tuple

from proxy_backend import ProxyBackend, ProxyBackendConfig


def _normalize_no_proxy(values: Iterable[Any]) -> Tuple[str, ...]:
    """Return stable, case-insensitive no-proxy entries without duplicates."""
    normalized = []
    seen = set()
    for raw in values:
        value = str(raw or "").strip().lower()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return tuple(normalized)


class WindowsBackend(ProxyBackend):
    """Concrete backend backed by the customer-proven Windows implementation.

    ``proxy_core`` is injected lazily so importing this module does not import
    Windows-specific implementation details.  Injection also keeps the adapter
    independently testable on non-Windows CI runners.

    The legacy Windows entry points currently read their own persisted settings.
    Therefore ``enable`` and ``sync_no_proxy`` delegate only when the supplied
    resolved config exactly matches what those entry points would apply.  This
    prevents the backend from reporting success for a configuration the legacy
    implementation would silently ignore.
    """

    def __init__(self, legacy_core=None):
        if legacy_core is None:
            import proxy_core as legacy_core  # local import avoids module coupling
        self._core = legacy_core

    @property
    def backend_id(self) -> str:
        return "windows"

    def _resolved_legacy_config(self) -> ProxyBackendConfig:
        settings = self._core.load_settings()
        port = int(settings.get("local_http_port", 8080))
        no_proxy = _normalize_no_proxy(
            list(getattr(self._core, "DEFAULT_NO_PROXY", ())) +
            list(self._core.load_no_proxy())
        )
        return ProxyBackendConfig(
            pac_url=str(self._core.pac_url(settings)),
            http_proxy_url="http://127.0.0.1:%d" % port,
            no_proxy=no_proxy,
        )

    def _config_matches_legacy_runtime(self, config: ProxyBackendConfig) -> bool:
        if not isinstance(config, ProxyBackendConfig):
            return False
        expected = self._resolved_legacy_config()
        actual = ProxyBackendConfig(
            pac_url=str(config.pac_url),
            http_proxy_url=str(config.http_proxy_url),
            no_proxy=_normalize_no_proxy(config.no_proxy),
        )
        return actual == expected

    def _log_config_mismatch(self, operation: str) -> None:
        logger = getattr(self._core, "_log", None)
        if callable(logger):
            logger(
                "WindowsBackend %s aborted: supplied config does not match "
                "the legacy Windows runtime configuration" % operation
            )

    def enable(self, config: ProxyBackendConfig) -> bool:
        if not self._config_matches_legacy_runtime(config):
            self._log_config_mismatch("enable")
            return False
        return bool(self._core.enable_system_proxy())

    def disable(self) -> bool:
        return bool(self._core.disable_system_proxy())

    def is_enabled(self, config: ProxyBackendConfig) -> bool:
        if not self._config_matches_legacy_runtime(config):
            return False
        return bool(self._core.system_proxy_enabled())

    def restore_pending(self) -> bool:
        return bool(self._core.network_restore_pending())

    def sync_no_proxy(self, config: ProxyBackendConfig) -> bool:
        if not self._config_matches_legacy_runtime(config):
            self._log_config_mismatch("sync_no_proxy")
            return False
        return bool(self._core.sync_client_no_proxy())
