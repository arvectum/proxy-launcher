"""Canonical proxy-core structured logging bridge for Arvectum Proxy Launcher.

Owns construction of the proxy-core ``StructuredLogger`` singleton and the public ``structured_log`` and ``_log`` surfaces. JSONL persistence, redaction and rotation remain owned by ``structured_logging.py``; logger resolution stays dynamic for supported runtime patchability.
"""

from __future__ import annotations

from types import ModuleType

from structured_logging import StructuredLogger


_CORE: ModuleType | None = None


def configure(core: ModuleType) -> None:
    """Bind the canonical composition module used for runtime collaborators."""
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
