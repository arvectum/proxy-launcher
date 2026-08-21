# -*- coding: utf-8 -*-
"""Mutable compatibility/state shell for the canonical Proxy Launcher core.

APL-IP-003 Slices 1–12 moved maintained runtime implementation into explicit
canonical owners and removed the duplicated legacy implementation body. This
module now retains only the narrow shared namespace still required before or
across canonical owner composition: release/state identity plus a shrinking set
of compatibility dependencies not yet decoupled from state-sensitive modules.

``proxy_core.py`` imports this module object, installs every canonical owner
onto it, and then exposes the same object as ``proxy_core``. Keeping that single
mutable object preserves the sealed 0.2.3 monkeypatch/import contract while
later slices progressively remove non-contractual dependency lookups.

No runtime function or class is implemented here. Historical implementation
remains available through Git history and provenance evidence.
"""

import base64
import hashlib
import io
import json
import os
import subprocess
import sys
import threading
import time


# Release identity consumed by the canonical logging bridge and release guards.
APP_VERSION = "0.2.3"
ENGINEERING_MILESTONE = "P0.2"

# State/bootstrap values used by application_filesystem before all owners have
# been installed. ``_STATE_READY`` remains mutable by design and is also an
# established test seam.
_STATE_FILES = (
    "proxy_settings.json",
    "no_proxy.txt",
    "proxy_core.pid",
    "proxy_core.log",
    "proxy_internet_backup.json",
    "proxy_env_backup.json",
)
_STATE_READY = False

# Portable/install identity required by application_filesystem,
# portable_lifecycle and Recovery Run ownership. Historical owner values are
# evidence/classification data only; retaining them does not relabel history.
_INSTALL_OWNER_MARKER = ".arvectum-install-owner"
_INSTALL_OWNER_VALUE = "ARVECTUM_PROXY_LAUNCHER_INSTALL_OWNER"
_LEGACY_INSTALL_OWNER_VALUES = {"ARVECTUM_PROXY_LAUNCHER_WINDOWS_RC2_1"}
_LAUNCHER_EXE_NAME = "Arvectum Proxy Launcher.exe"
_USER_AUTOSTART_RUN_VALUE = "ArvectumProxyLauncher"
_LAST_SELF_HEAL_ERROR = ""
