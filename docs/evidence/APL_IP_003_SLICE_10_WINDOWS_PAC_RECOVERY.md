# APL-IP-003 Slice 10 — stale/orphan PAC diagnostics and cleanup ownership extraction evidence

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Canonical merge

- Pull request: `#136` — `APL-IP-003 Slice 10 — stale/orphan PAC recovery extraction`
- Merge commit: `82cec6776306c991b53029ac27e6864235201704`
- Pre-slice main baseline: `e7148202a8fbede6aed0559a74e066f694fbd51a`
- Reviewed final PR head: `e20b1c362bf9287bd57cd92db2b2e55ed0eb1d24`
- Product version: unchanged (`0.2.3`)
- Final implementation diff changed exactly four files: `.github/workflows/apl-ip-003-canonical-source.yml`, `proxy_core.py`, `tests/test_windows_pac_recovery.py`, and `windows_pac_recovery.py`.
- `proxy_core_legacy.py` was not edited.

## Extracted ownership

`windows_pac_recovery.py` is now the canonical owner for the bounded Windows stale/orphan PAC recovery path:

- `_any_known_internet_backup_exists` — destructive-cleanup ambiguity evidence across current and legacy Internet backup locations;
- `stale_system_proxy` — safe diagnostic state for an enabled owned PAC without a running engine or pending recovery;
- `orphaned_arvectum_pac` — exact fail-closed eligibility for a dead Arvectum localhost PAC;
- `_write_orphaned_pac_snapshot` — durable pre-cleanup Internet Settings evidence;
- `clear_orphaned_arvectum_pac` — race-safe deletion of only the exact owned `AutoConfigURL` followed by refresh and verification.

The owner is installed after `system_proxy_runtime` composition and before `application_runtime`. It therefore consumes the final composed Windows proxy status while dynamically delegating WinINET reads/deletes/refresh to the already canonical Slice 8 owner and process/listener/canonical-install evidence to their established canonical owners.

## Responsibilities deliberately not moved

Slice 10 does not take ownership of:

- WinINET backup creation/validation/restore;
- registry mutation primitives generally;
- proxy environment backup/restore;
- PAC URL construction or exact structural matcher implementation;
- process/PID ownership;
- PAC listener ownership;
- canonical portable-install detection;
- Recovery Run/autostart classification or mutation;
- GUI ordinary user-autostart implementation.

Those responsibilities remain with their existing canonical or deliberately separate owners.

## Behaviour contract preserved

The sealed Windows `0.2.3` recovery contract remains the reference. Slice 10 preserves all of the following:

- stale proxy state is diagnostic only and requires an enabled owned system PAC, no running owned engine, no pending network recovery, and no migration block;
- orphan cleanup is Windows-only;
- a migration conflict blocks cleanup;
- `AutoConfigURL` must exist and pass the exact structural Arvectum PAC matcher;
- an active compatible PAC listener blocks cleanup;
- an owned running engine blocks cleanup;
- **any** known current or legacy Internet backup file blocks cleanup, even when the file is invalid or unreadable, because its existence is ownership ambiguity evidence;
- an available canonical Documents installation blocks cleanup by a non-canonical copy;
- cleanup eligibility is re-evaluated before mutation;
- the registry is read again immediately before mutation and any changed/non-owned `AutoConfigURL` aborts cleanup as a race;
- a durable diagnostic snapshot is mandatory before registry deletion;
- failure to write that snapshot authorizes no mutation;
- only `AutoConfigURL` is deleted; `ProxyEnable`, `ProxyServer`, `ProxyOverride`, `AutoDetect`, proxy-environment variables, and unrelated network state are untouched;
- delete failure is reported as incomplete and is not followed by a false success;
- WinINET refresh occurs only after successful deletion;
- post-delete `system_proxy_enabled()` verification is mandatory;
- a still-active PAC after deletion is reported as incomplete;
- cleanup returns success only after exact deletion plus refresh plus postcondition verification.

## Compatibility and composition

All mutable collaborators continue to be resolved through the established `proxy_core` compatibility seam. Existing tests can therefore monkeypatch `_read_internet_settings`, `_exact_arvectum_pac_url`, `_known_internet_backup_paths`, `proxy_listener_active`, `is_running`, `canonical_install_exe`, `_reg_del`, `_refresh_internet`, and `system_proxy_enabled` exactly as before the extraction.

During self-review a transient extra facade alias was introduced while simplifying `proxy_core.py`; it was removed before the reviewed PR head. The final diff adds no new public facade surface beyond installing the canonical Slice 10 functions.

Historical implementation remains intact in `proxy_core_legacy.py` as truthful provenance evidence. The extraction changes current executable ownership, not historical authorship records.

## Targeted regression coverage

`tests/test_windows_pac_recovery.py` verifies:

- canonical source ownership of every extracted Slice 10 function;
- invalid backup-file existence still blocks destructive orphan cleanup;
- stale-system-proxy diagnostic gating;
- exact dead owned PAC eligibility;
- fail-closed behavior for non-Windows, migration conflict, active listener, running process, backup evidence and canonical-install evidence;
- rejection of foreign/similar/query-modified PAC URLs;
- snapshot-before-delete-before-refresh ordering;
- deletion of only `AutoConfigURL` while preserving manual proxy values;
- registry-race abort before snapshot/delete;
- mandatory durable snapshot before mutation;
- delete failure and still-active-PAC failure never claim success;
- snapshot location/content and exact pre-cleanup state evidence.

The APL-IP-003 canonical-source workflow was extended to compile `windows_pac_recovery.py` and execute this suite on Ubuntu, macOS and Windows together with the prior canonical ownership suites.

## Independent full-suite evidence

The pre-existing orphan/recovery/foreign-proxy tests were not rewritten to depend on the new module. `Phase 5 Config and Security` completed successfully on both Ubuntu and Windows and ran the full `python -m unittest discover -s tests -v` suite.

Additional diagnostics/logging workflows also independently ran their full unit suites successfully. This demonstrates that the extraction preserves the existing `proxy_core` behavior observed by older tests rather than merely satisfying new Slice 10 tests.

## Implementation PR workflow evidence — 18/18 SUCCESS

- `32494685666` — APL-LNX-006 Linux diagnostics support bundle
- `32494685814` — Secret scan
- `32494685589` — APL-IP-001 provenance
- `32494685693` — Phase 5 Config and Security
- `32494685894` — APL-LNX-007 Debian package
- `32494685564` — Core backend contract
- `32494685700` — SBOM
- `32494685758` — Dependency vulnerability scan
- `32494685678` — APL-IP-003 canonical source
- `32494685724` — SAST
- `32494685572` — APL-DIAG-004 Doctor
- `32494685461` — APL-LNX-008 AppImage
- `32494685810` — macOS packaging
- `32494685705` — Windows P0 portable
- `32494685914` — APL-DIAG-003/006 Windows diagnostics + privacy
- `32494685626` — APL-IP-002-WIN controlled offline build
- `32494685670` — APL-DIAG-001/002 structured logging + secret redaction
- `32494685853` — Windows installer

## Release / packaging evidence

- Canonical-source compile + targeted regression: Ubuntu, macOS and Windows — SUCCESS.
- Full Phase 5 unit regression: Ubuntu and Windows — SUCCESS.
- Structured logging/redaction full unit regression: Ubuntu and Windows — SUCCESS.
- Windows diagnostics/privacy full unit regression: Ubuntu and Windows — SUCCESS.
- Windows P0 portable canonical build + Documents smoke — SUCCESS.
- Windows installer fresh/upgrade/repair/uninstall E2E and Gate R6 — SUCCESS.
- Controlled offline Windows build — SUCCESS, including verified CPython/wheelhouse acquisition, offline canonical portable build and explicit no-package-index-fallback proof.
- macOS package, Debian package and AppImage package gates — SUCCESS.
- SAST, dependency vulnerability, secret scan, provenance, SBOM, backend and doctor gates — SUCCESS.

## Governance

This evidence establishes engineering completion of Slice 10 only. It does **not** declare clean-IP APPROVED and does not authorize a clean-IP tag.

The author-to-ООО rights-basis execution/reconciliation remains HUMAN/LEGAL PENDING under the standing APL-IP-001/APL-IP-003 governance gate. Git history, AI-assistance evidence and automation identities remain unaltered and have not been reassigned.

## Next bounded slice

**APL-IP-003 Slice 11 — structured logging bridge ownership extraction.**

Planned bounded ownership: canonical construction of the `StructuredLogger` used by core plus `structured_log()` and the `_log()` compatibility sink. Exact `APP_VERSION`, `ENGINEERING_MILESTONE`, component metadata, path resolution through `log_path()`, dynamic monkeypatch compatibility and never-raise-on-log-I/O semantics must remain unchanged.

Platform predicates/runtime identity, GUI user-autostart/Task Scheduler implementation and other remaining legacy foundations stay separate later slices.
