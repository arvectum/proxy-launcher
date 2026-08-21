"""Canonical stale/orphan Windows PAC recovery for Arvectum Proxy Launcher.

APL-IP-003 Slice 10 owns the narrowly bounded diagnostic and cleanup path for
an Arvectum localhost PAC that remains configured after its owning runtime and
rollback evidence are gone.  The implementation preserves the sealed Windows
0.2.3 fail-closed contract: exact PAC ownership alone is insufficient for
cleanup, any backup/migration/listener/process/canonical-instance evidence
blocks mutation, a durable snapshot is required before registry deletion, and
the exact registry value is revalidated immediately before mutation.

WinINET persistence/mutation primitives remain owned by ``windows_system_proxy``;
process/listener ownership remains in ``process_supervision`` and
``local_proxy_transport``; canonical-install detection remains in the
filesystem/portable lifecycle layers.
"""

from __future__ import annotations

import io
import json
import os
import time
from types import ModuleType


_CORE: ModuleType | None = None


def configure(core: ModuleType) -> None:
    """Bind the established mutable core compatibility seam."""
    global _CORE
    _CORE = core


def _core() -> ModuleType:
    if _CORE is None:
        raise RuntimeError("Windows PAC recovery is not configured")
    return _CORE


def _any_known_internet_backup_exists():
    """Treat any current/legacy backup file as destructive-cleanup evidence.

    Even an invalid or unreadable backup means ownership is ambiguous.  This
    predicate deliberately checks existence only; validity is irrelevant to the
    orphan-cleanup decision.
    """
    core = _core()
    return any(os.path.exists(path) for path in core._known_internet_backup_paths())


def stale_system_proxy():
    """Report a configured owned PAC with no live engine or rollback evidence."""
    core = _core()
    return (
        core.system_proxy_enabled()
        and not core.is_running()
        and not core.network_restore_pending()
        and not core.state_migration_blocked()
    )


def orphaned_arvectum_pac():
    """Return True only for the narrowly proven dead Arvectum localhost PAC."""
    core = _core()
    if not core.is_windows() or core.state_migration_blocked():
        return False
    values = core._read_internet_settings()
    item = (values or {}).get("AutoConfigURL") or {}
    if not item.get("exists") or not core._exact_arvectum_pac_url(item.get("value")):
        return False
    if core.proxy_listener_active() or core.is_running():
        return False
    if core._any_known_internet_backup_exists():
        return False
    # A non-canonical copy must hand off to the owned Documents install.  It is
    # never allowed to clean shared WinINET state while that owner is available.
    if core.canonical_install_exe():
        return False
    return True


def _write_orphaned_pac_snapshot(values):
    """Persist the exact pre-cleanup Internet Settings evidence."""
    core = _core()
    try:
        os.makedirs(core.data_dir(), exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S") + "-%d" % int(time.time() * 1000 % 1000)
        path = os.path.join(core.data_dir(), "orphaned_arvectum_pac_%s.json" % stamp)
        snapshot = {
            "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "reason": "orphaned_arvectum_pac",
            "internet_settings": values,
            "expected_pac_url": core.pac_url(core.load_settings()),
        }
        with io.open(path, "w", encoding="utf-8") as stream:
            json.dump(snapshot, stream, ensure_ascii=False, indent=2)
        return path
    except Exception as exc:
        core._log("orphan PAC diagnostic snapshot error: %r" % exc)
        return None


def clear_orphaned_arvectum_pac():
    """Delete only a re-verified dead Arvectum ``AutoConfigURL`` entry.

    This is intentionally not a network reset and never changes manual proxy
    values or user proxy-environment variables.  Registry drift between
    eligibility and mutation is a race and aborts cleanup.
    """
    core = _core()
    if not core.orphaned_arvectum_pac():
        core._log("orphan PAC cleanup skipped: ownership conditions are not proven")
        return False

    # Re-read immediately before mutation.  Eligibility may have been true a
    # moment ago while another process has since changed the shared registry.
    values = core._read_internet_settings()
    item = (values or {}).get("AutoConfigURL") or {}
    if not item.get("exists") or not core._exact_arvectum_pac_url(item.get("value")):
        core._log("orphan PAC cleanup aborted: AutoConfigURL changed before mutation")
        return False
    if not core._write_orphaned_pac_snapshot(values):
        core._log("orphan PAC cleanup aborted: diagnostic snapshot was not written")
        return False
    if not core._reg_del("AutoConfigURL"):
        core._log("orphan PAC cleanup incomplete: AutoConfigURL delete failed")
        return False

    core._refresh_internet()
    if core.system_proxy_enabled():
        core._log("orphan PAC cleanup incomplete: PAC is still active")
        return False
    core._log("orphan Arvectum PAC removed safely")
    return True


def install_into_core(core: ModuleType) -> ModuleType:
    """Expose canonical stale/orphan PAC recovery through ``proxy_core``."""
    configure(core)
    for name in (
        "_any_known_internet_backup_exists",
        "stale_system_proxy",
        "orphaned_arvectum_pac",
        "_write_orphaned_pac_snapshot",
        "clear_orphaned_arvectum_pac",
    ):
        setattr(core, name, globals()[name])
    return core
