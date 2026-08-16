# -*- coding: utf-8 -*-
"""Automatic operating-system backend selection for Arvectum Proxy Launcher.

APL-CORE-005 keeps platform detection in one small composition layer. Concrete
backends remain independently testable and are imported only for the selected
platform.

APL-CORE-006 binds the selected backend to one explicit capability model so UI
and callers do not infer feature support independently from ``sys.platform``.

APL-LNX-003 adds a runtime operational gate for Linux/Astra. Static product
support and host readiness are deliberately separate concepts: Linux can be a
supported product platform while a particular host is not currently safe to
mutate through NetworkManager.
"""

from dataclasses import dataclass
from enum import Enum
import sys

from capability_model import capabilities_for_backend


class UnsupportedPlatformError(RuntimeError):
    """Raised when no governed system-proxy backend exists for this platform."""


class OperationalState(str, Enum):
    READY = "ready"
    AUTH_REQUIRED = "auth_required"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class BackendOperationalStatus:
    backend_id: str
    platform_label: str
    state: OperationalState
    can_enable: bool
    title: str
    message: str
    reasons: tuple = ()


class BackendOperationalError(RuntimeError):
    """Raised when a new proxy mutation is unsafe on the current host."""

    def __init__(self, status):
        self.status = status
        super().__init__(status.message or status.title)


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


def _always_ready_status(backend_id):
    platform = capabilities_for_backend(backend_id)
    return BackendOperationalStatus(
        backend_id=backend_id,
        platform_label=platform.platform_label,
        state=OperationalState.READY,
        can_enable=True,
        title="Системный прокси доступен",
        message="Платформа готова к применению системных настроек Arvectum.",
        reasons=(),
    )


def operational_status_for_platform(platform=None, linux_preflight=None):
    """Return host-specific readiness without mutating network state.

    Windows/macOS currently have their own backend validation paths and therefore
    remain operationally ready here. Linux/Astra delegates to APL-LNX-002.
    ``linux_preflight`` is an injectable result used by deterministic tests.
    """
    backend_id = backend_id_for_platform(platform)
    if backend_id != "linux":
        return _always_ready_status(backend_id)

    if linux_preflight is None:
        from linux_networkmanager_preflight import detect_networkmanager_preflight
        linux_preflight = detect_networkmanager_preflight()

    from linux_networkmanager_preflight import PreflightStatus

    reasons = tuple(getattr(linux_preflight, "reasons", ()) or ())
    preflight_state = getattr(linux_preflight, "status", None)
    platform_label = capabilities_for_backend("linux").platform_label

    if preflight_state == PreflightStatus.READY:
        return BackendOperationalStatus(
            backend_id="linux",
            platform_label=platform_label,
            state=OperationalState.READY,
            can_enable=True,
            title="NetworkManager готов",
            message="Linux/Astra готов к безопасному применению системного прокси Arvectum.",
            reasons=reasons,
        )
    if preflight_state == PreflightStatus.AUTH_REQUIRED:
        return BackendOperationalStatus(
            backend_id="linux",
            platform_label=platform_label,
            state=OperationalState.AUTH_REQUIRED,
            can_enable=False,
            title="Требуется разрешение NetworkManager",
            message=(
                "NetworkManager поддерживает необходимые настройки, но текущему пользователю "
                "нужно отдельное разрешение PolicyKit. Arvectum не будет менять сеть без него."
            ),
            reasons=reasons,
        )
    return BackendOperationalStatus(
        backend_id="linux",
        platform_label=platform_label,
        state=OperationalState.UNAVAILABLE,
        can_enable=False,
        title="Системный прокси недоступен",
        message=(
            "На этом Linux/Astra-хосте NetworkManager сейчас не готов к безопасному "
            "применению системного прокси. Сеть оставлена без изменений."
        ),
        reasons=reasons,
    )


def operational_status_view(status):
    """Stable user-facing data for Linux/Astra capability UX."""
    if not isinstance(status, BackendOperationalStatus):
        raise TypeError("BackendOperationalStatus is required")
    badge = {
        OperationalState.READY: "Доступно",
        OperationalState.AUTH_REQUIRED: "Нужно разрешение",
        OperationalState.UNAVAILABLE: "Недоступно",
    }[status.state]
    return {
        "backend_id": status.backend_id,
        "platform_label": status.platform_label,
        "state": status.state.value,
        "badge": badge,
        "enabled": bool(status.can_enable),
        "title": status.title,
        "message": status.message,
        "reasons": tuple(status.reasons),
    }


def require_enable_operational(platform=None, linux_preflight=None):
    """Fail closed before a new proxy mutation when host preflight is not ready."""
    status = operational_status_for_platform(platform, linux_preflight=linux_preflight)
    if not status.can_enable:
        raise BackendOperationalError(status)
    return status


def create_backend(platform=None, legacy_core=None, logger=None):
    """Instantiate the concrete backend selected for *platform*.

    Selection itself stays side-effect free and does not run operational
    preflight. Callers gate new mutations through ``require_enable_operational``.
    This separation is intentional: recovery/disable must remain reachable even
    when a later host preflight is degraded.

    Windows deliberately receives the captured legacy implementation from the
    runtime facade. This prevents the Windows adapter from recursively calling
    the new public dispatch functions while preserving the customer-proven
    Windows 0.2.3 mutation path byte-for-byte.
    """
    backend_id = backend_id_for_platform(platform)
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
