# -*- coding: utf-8 -*-
"""Side-effect-free macOS runtime detection for APL-MAC-001."""
from dataclasses import dataclass
import os
import platform as platform_module
import shutil
import sys
from typing import Callable, Mapping, Optional


class MacOSRuntimeDetectionError(RuntimeError):
    pass


@dataclass(frozen=True)
class MacOSRuntimeEnvironment:
    product_version: str
    build_version: str
    architecture: str
    networksetup_path: str
    launchctl_path: str
    hdiutil_path: str
    session_user: str

    @property
    def networksetup_available(self):
        return bool(self.networksetup_path)


def detect_macos_runtime(
    *,
    platform_name: Optional[str] = None,
    environ: Optional[Mapping[str, str]] = None,
    which: Callable[[str], Optional[str]] = shutil.which,
    mac_ver: Callable[[], tuple] = platform_module.mac_ver,
    machine: Callable[[], str] = platform_module.machine,
) -> MacOSRuntimeEnvironment:
    current = str(sys.platform if platform_name is None else platform_name).lower()
    if current != "darwin":
        raise MacOSRuntimeDetectionError("macOS runtime detection requires darwin")
    version_info = mac_ver()
    version = str(version_info[0] if version_info else "")
    release = version_info[1] if len(version_info) > 1 else ()
    build_version = ""
    if isinstance(release, (tuple, list)) and release:
        build_version = ".".join(str(v) for v in release if str(v))
    values = os.environ if environ is None else environ
    return MacOSRuntimeEnvironment(
        product_version=version,
        build_version=build_version,
        architecture=str(machine() or ""),
        networksetup_path=str(which("networksetup") or ("/usr/sbin/networksetup" if os.path.exists("/usr/sbin/networksetup") else "")),
        launchctl_path=str(which("launchctl") or ("/bin/launchctl" if os.path.exists("/bin/launchctl") else "")),
        hdiutil_path=str(which("hdiutil") or ("/usr/bin/hdiutil" if os.path.exists("/usr/bin/hdiutil") else "")),
        session_user=str(values.get("USER", "") or ""),
    )
