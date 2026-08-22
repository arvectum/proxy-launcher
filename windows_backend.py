# -*- coding: utf-8 -*-
"""Windows implementation of the ProxyBackend contract.

the Windows backend adapter introduced this compatibility backend around the proven Windows
0.2.3 behaviour. WinINET, per-user proxy-environment persistence and Windows system-proxy mutation
are owned by ``windows_system_proxy``;
``system_proxy_runtime`` injects the captured canonical implementation here
through the established compatibility adapter.
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

    The implementation seam is injected lazily so importing this module does
    not import Windows-specific mutation details. Injection also keeps the
    adapter independently testable on non-Windows CI runners.

    The Windows entry points read their own persisted settings. Therefore
    ``enable`` and ``sync_no_proxy`` delegate only when the supplied resolved
    config exactly matches what those entry points would apply. This prevents
    the backend from reporting success for a configuration the canonical
    implementation would silently ignore.

    Private helper names describe the current runtime adapter and configuration
    comparison boundary directly.
    """

    def __init__(self, runtime_core=None):
        if runtime_core is None:
            import proxy_core as runtime_core  # local import avoids module coupling
        self._core = runtime_core

    @property
    def backend_id(self) -> str:
        return "windows"

    def _resolved_runtime_config(self) -> ProxyBackendConfig:
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

    def _config_matches_runtime(self, config: ProxyBackendConfig) -> bool:
        if not isinstance(config, ProxyBackendConfig):
            return False
        expected = self._resolved_runtime_config()
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
                "the current Windows runtime configuration" % operation
            )

    def enable(self, config: ProxyBackendConfig) -> bool:
        if not self._config_matches_runtime(config):
            self._log_config_mismatch("enable")
            return False
        return bool(self._core.enable_system_proxy())

    def disable(self) -> bool:
        return bool(self._core.disable_system_proxy())

    def is_enabled(self, config: ProxyBackendConfig) -> bool:
        if not self._config_matches_runtime(config):
            return False
        return bool(self._core.system_proxy_enabled())

    def restore_pending(self) -> bool:
        return bool(self._core.network_restore_pending())

    def sync_no_proxy(self, config: ProxyBackendConfig) -> bool:
        if not self._config_matches_runtime(config):
            self._log_config_mismatch("sync_no_proxy")
            return False
        return bool(self._core.sync_client_no_proxy())
