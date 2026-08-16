# -*- coding: utf-8 -*-
"""Read-only NetworkManager operational capability detection for Linux/Astra.

APL-LNX-002 turns APL-LNX-001 runtime facts into an explicit readiness verdict
for the NetworkManager backend. The preflight never modifies connections,
starts services, reloads NetworkManager, or requests elevated privileges.
"""

from dataclasses import dataclass
from enum import Enum
import re
import subprocess
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple

from linux_runtime import LinuxRuntimeEnvironment, detect_linux_runtime


class PreflightStatus(str, Enum):
    READY = "ready"
    AUTH_REQUIRED = "auth_required"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class NetworkManagerPreflight:
    runtime: LinuxRuntimeEnvironment
    status: PreflightStatus
    nmcli_version: str
    networkmanager_state: str
    connectivity: str
    active_connection_uuids: Tuple[str, ...]
    supported_active_connection_uuids: Tuple[str, ...]
    proxy_setting_supported: bool
    modify_system_permission: str
    modify_own_permission: str
    reasons: Tuple[str, ...]

    @property
    def operational(self) -> bool:
        return self.status == PreflightStatus.READY

    @property
    def can_attempt_with_authorization(self) -> bool:
        return self.status in {PreflightStatus.READY, PreflightStatus.AUTH_REQUIRED}


class NetworkManagerPreflightError(RuntimeError):
    """Raised only for malformed injected execution results."""


_IGNORED_ACTIVE_TYPES = frozenset({"vpn", "loopback"})
_PERMISSION_SYSTEM = "org.freedesktop.NetworkManager.settings.modify.system"
_PERMISSION_OWN = "org.freedesktop.NetworkManager.settings.modify.own"
_PERMISSION_VALUES = frozenset({"yes", "auth", "no", "unknown"})


def _default_runner(arguments: Sequence[str], timeout: int = 10) -> Any:
    return subprocess.run(
        list(arguments),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        timeout=timeout,
        env={"LC_ALL": "C", "LANG": "C"},
    )


def _run_readonly(
    runner: Callable[..., Any], binary: str, *arguments: str
) -> Tuple[int, str, str]:
    try:
        completed = runner([binary] + list(arguments), timeout=10)
    except TypeError:
        completed = runner([binary] + list(arguments))
    except Exception as exc:
        return 127, "", str(exc)
    try:
        returncode = int(getattr(completed, "returncode", 1))
    except Exception as exc:
        raise NetworkManagerPreflightError("invalid runner return code") from exc
    return (
        returncode,
        str(getattr(completed, "stdout", "") or "").strip(),
        str(getattr(completed, "stderr", "") or "").strip(),
    )


def _parse_nmcli_version(text: str) -> str:
    match = re.search(r"(?:nmcli tool, version|nmcli)\s+([^\s]+)", str(text or ""), re.I)
    return match.group(1) if match else str(text or "").strip()


def _parse_permissions(text: str) -> Mapping[str, str]:
    result = {}
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ":" in line:
            permission, value = line.rsplit(":", 1)
        elif " " in line:
            permission, value = line.rsplit(None, 1)
        else:
            continue
        value = value.strip().lower()
        if value not in _PERMISSION_VALUES:
            value = "unknown"
        result[permission.strip()] = value
    return result


def _parse_active_connections(text: str) -> Tuple[Tuple[str, str, str], ...]:
    rows = []
    seen = set()
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        fields = line.split(":", 2)
        if len(fields) != 3:
            continue
        uuid, connection_type, device = (field.strip() for field in fields)
        if not uuid or uuid in seen:
            continue
        seen.add(uuid)
        rows.append((uuid, connection_type.lower(), device))
    return tuple(rows)


def detect_networkmanager_preflight(
    *,
    runtime: Optional[LinuxRuntimeEnvironment] = None,
    runner: Callable[..., Any] = _default_runner,
) -> NetworkManagerPreflight:
    """Return a read-only NetworkManager backend readiness verdict.

    READY requires: nmcli present, daemon reachable, at least one supported active
    managed connection, proxy profile properties readable, and non-interactive
    permission to modify either system or own connection profiles.

    AUTH_REQUIRED is used when all technical capabilities exist but PolicyKit
    reports ``auth`` rather than ``yes`` for the relevant modification permission.
    """
    detected_runtime = runtime or detect_linux_runtime()
    reasons = []
    binary = detected_runtime.nmcli_path
    if not binary:
        return NetworkManagerPreflight(
            runtime=detected_runtime,
            status=PreflightStatus.UNAVAILABLE,
            nmcli_version="",
            networkmanager_state="unavailable",
            connectivity="unknown",
            active_connection_uuids=(),
            supported_active_connection_uuids=(),
            proxy_setting_supported=False,
            modify_system_permission="unknown",
            modify_own_permission="unknown",
            reasons=("nmcli client is not installed or not discoverable",),
        )

    rc, stdout, stderr = _run_readonly(runner, binary, "--version")
    nmcli_version = _parse_nmcli_version(stdout) if rc == 0 else ""
    if rc != 0:
        reasons.append("nmcli executable cannot be queried")

    rc_state, state_out, state_err = _run_readonly(
        runner, binary, "--terse", "--fields", "STATE,CONNECTIVITY", "general", "status"
    )
    networkmanager_state = "unavailable"
    connectivity = "unknown"
    if rc_state == 0 and state_out:
        first = state_out.splitlines()[0]
        parts = first.split(":", 1)
        networkmanager_state = parts[0].strip().lower() or "unknown"
        if len(parts) == 2:
            connectivity = parts[1].strip().lower() or "unknown"
    else:
        reasons.append("NetworkManager daemon is not reachable through nmcli")
        if state_err:
            reasons.append("nmcli general status failed")

    rc_active, active_out, _ = _run_readonly(
        runner,
        binary,
        "--terse",
        "--escape",
        "no",
        "--fields",
        "UUID,TYPE,DEVICE",
        "connection",
        "show",
        "--active",
    )
    active_rows = _parse_active_connections(active_out) if rc_active == 0 else ()
    active_uuids = tuple(row[0] for row in active_rows)
    supported_rows = tuple(
        row for row in active_rows
        if row[1] not in _IGNORED_ACTIVE_TYPES and row[2] and row[2] != "--"
    )
    supported_uuids = tuple(row[0] for row in supported_rows)
    if rc_state == 0 and not supported_rows:
        reasons.append("no supported active NetworkManager connection profiles found")

    proxy_setting_supported = False
    if supported_rows:
        probe_uuid = supported_rows[0][0]
        proxy_ok = True
        for property_name in (
            "proxy.method",
            "proxy.browser-only",
            "proxy.pac-url",
            "proxy.pac-script",
        ):
            rc_proxy, _, _ = _run_readonly(
                runner,
                binary,
                "--escape",
                "no",
                "--get-values",
                property_name,
                "connection",
                "show",
                "uuid",
                probe_uuid,
            )
            if rc_proxy != 0:
                proxy_ok = False
                break
        proxy_setting_supported = proxy_ok
        if not proxy_ok:
            reasons.append("active NetworkManager profile does not expose required proxy properties")

    rc_perm, perm_out, _ = _run_readonly(
        runner,
        binary,
        "--terse",
        "--fields",
        "PERMISSION,VALUE",
        "general",
        "permissions",
    )
    permissions = _parse_permissions(perm_out) if rc_perm == 0 else {}
    system_permission = permissions.get(_PERMISSION_SYSTEM, "unknown")
    own_permission = permissions.get(_PERMISSION_OWN, "unknown")
    if rc_perm != 0:
        reasons.append("NetworkManager modification permissions cannot be determined")

    technical_ready = (
        rc == 0
        and rc_state == 0
        and bool(supported_rows)
        and proxy_setting_supported
        and rc_perm == 0
    )
    permission_values = {system_permission, own_permission}
    if technical_ready and "yes" in permission_values:
        status = PreflightStatus.READY
    elif technical_ready and "auth" in permission_values:
        status = PreflightStatus.AUTH_REQUIRED
        reasons.append("NetworkManager modification requires PolicyKit authorization")
    else:
        status = PreflightStatus.UNAVAILABLE
        if technical_ready and permission_values <= {"no", "unknown"}:
            reasons.append("current user is not permitted to modify NetworkManager profiles")

    return NetworkManagerPreflight(
        runtime=detected_runtime,
        status=status,
        nmcli_version=nmcli_version,
        networkmanager_state=networkmanager_state,
        connectivity=connectivity,
        active_connection_uuids=active_uuids,
        supported_active_connection_uuids=supported_uuids,
        proxy_setting_supported=proxy_setting_supported,
        modify_system_permission=system_permission,
        modify_own_permission=own_permission,
        reasons=tuple(dict.fromkeys(reasons)),
    )
