"""Canonical proxy-core structured logging bridge for Arvectum Proxy Launcher.

APL-IP-003 Slice 11 owns construction of the proxy-core ``StructuredLogger``
singleton plus the established ``structured_log`` and ``_log`` compatibility
surfaces.  The lower-level JSONL/redaction/rotation implementation remains in
``structured_logging.py`` under its existing diagnostics contract.

The bridge deliberately resolves the logger and compatibility function through
the mutable core module at call time.  This preserves the sealed 0.2.3
monkeypatch seams while moving implementation ownership out of
``proxy_core_legacy.py``.
"""

from __future__ import annotations

from types import ModuleType

from structured_logging import StructuredLogger


_CORE: ModuleType | None = None


def configure(core: ModuleType) -> None:
    """Bind the established mutable proxy-core compatibility seam."""
    global _CORE
    _CORE = core


def _core() -> ModuleType:
    if _CORE is None:
        raise RuntimeError("Logging bridge is not configured")
    return _CORE


def _build_structured_logger(core: ModuleType) -> StructuredLogger:
    """Construct the exact historical proxy-core logger metadata contract."""
    return StructuredLogger(
        path_getter=lambda: core.log_path(),
        app_version=core.APP_VERSION,
        milestone=core.ENGINEERING_MILESTONE,
        component="proxy_core",
    )


def structured_log(message, level=None, event=None, **fields):
    """Write one structured diagnostic event; never raises on log I/O failure."""
    core = _core()
    return core.structured_logger.log(
        message,
        level=level,
        event=event,
        fields=fields or None,
    )


def _log(msg):
    """Backward-compatible sink for existing call sites."""
    return _core().structured_log(msg)


def install_into_core(core: ModuleType) -> ModuleType:
    """Install the canonical singleton and compatibility functions into core."""
    configure(core)
    core.structured_logger = _build_structured_logger(core)
    core.structured_log = structured_log
    core._log = _log
    return core
