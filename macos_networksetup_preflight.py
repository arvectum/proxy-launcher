# -*- coding: utf-8 -*-
"""Read-only networksetup readiness detection for the macOS networksetup preflight."""
from dataclasses import dataclass
from enum import Enum
import subprocess
from typing import Any, Callable, Optional, Sequence, Tuple

from macos_runtime import MacOSRuntimeEnvironment, detect_macos_runtime


class MacOSPreflightStatus(str, Enum):
    READY = "ready"
    AUTH_REQUIRED = "auth_required"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class MacOSNetworkPreflight:
    runtime: MacOSRuntimeEnvironment
    status: MacOSPreflightStatus
    enabled_services: Tuple[str, ...]
    readable_services: Tuple[str, ...]
    reasons: Tuple[str, ...]


def _runner(arguments: Sequence[str], timeout: int = 10) -> Any:
    return subprocess.run(list(arguments), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=timeout)


def _run(runner: Callable[..., Any], args: Sequence[str]):
    try:
        result = runner(list(args), timeout=10)
    except TypeError:
        result = runner(list(args))
    except Exception as exc:
        return 127, "", str(exc)
    return int(getattr(result, "returncode", 1)), str(getattr(result, "stdout", "") or ""), str(getattr(result, "stderr", "") or "")


def _services(text: str) -> Tuple[str, ...]:
    values = []
    for raw in str(text or "").splitlines():
        line = raw.strip()
        if not line or "denotes that a network service is disabled" in line.lower() or line.startswith("*"):
            continue
        if line not in values:
            values.append(line)
    return tuple(values)


def detect_macos_network_preflight(*, runtime: Optional[MacOSRuntimeEnvironment] = None, runner: Callable[..., Any] = _runner) -> MacOSNetworkPreflight:
    detected = runtime or detect_macos_runtime()
    binary = detected.networksetup_path
    if not binary:
        return MacOSNetworkPreflight(detected, MacOSPreflightStatus.UNAVAILABLE, (), (), ("networksetup is unavailable",))
    rc, out, err = _run(runner, [binary, "-listallnetworkservices"])
    if rc != 0:
        detail = "networksetup cannot enumerate network services"
        if "not authorized" in (out + err).lower() or "authorization" in (out + err).lower():
            return MacOSNetworkPreflight(detected, MacOSPreflightStatus.AUTH_REQUIRED, (), (), (detail,))
        return MacOSNetworkPreflight(detected, MacOSPreflightStatus.UNAVAILABLE, (), (), (detail,))
    enabled = _services(out)
    if not enabled:
        return MacOSNetworkPreflight(detected, MacOSPreflightStatus.UNAVAILABLE, (), (), ("no enabled macOS network services found",))
    readable = []
    reasons = []
    auth_seen = False
    for service in enabled:
        rc_auto, auto_out, auto_err = _run(runner, [binary, "-getautoproxyurl", service])
        rc_bypass, bypass_out, bypass_err = _run(runner, [binary, "-getproxybypassdomains", service])
        combined = "\n".join((auto_out, auto_err, bypass_out, bypass_err)).lower()
        if rc_auto == 0 and rc_bypass == 0:
            readable.append(service)
        elif "not authorized" in combined or "authorization" in combined or "administrator" in combined:
            auth_seen = True
        else:
            reasons.append("proxy state is unreadable for network service: %s" % service)
    if len(readable) == len(enabled):
        status = MacOSPreflightStatus.READY
    elif auth_seen and not reasons:
        status = MacOSPreflightStatus.AUTH_REQUIRED
        reasons.append("macOS authorization is required to inspect proxy state")
    else:
        status = MacOSPreflightStatus.UNAVAILABLE
    return MacOSNetworkPreflight(detected, status, enabled, tuple(readable), tuple(dict.fromkeys(reasons)))
