# APL-IP-003 Slice 6 — process supervision ownership extraction evidence

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Canonical merge

- Pull request: `#128` — `APL-IP-003 Slice 6 — process supervision ownership extraction`
- Merge commit: `82333217bb992c00c22663d5b636f90252c05171`
- Pre-slice main baseline: `755bd68ed0abc9e1bf2a5623517d2c9edd755f0b`
- Reviewed PR head: `deb951cdf5cf13a86c06169de33362a1ea0a1bc9`
- Product version: unchanged (`0.2.3`)

## Extracted ownership

`process_supervision.py` is now the canonical process-supervision/runtime-status implementation owner, through the established mutable `proxy_core` compatibility seam, for:

- `_pac_healthy` — local PAC endpoint health probing;
- `proxy_listener_active` — compatible listener diagnostics without ownership inference;
- `_windows_process_creation_time` — Windows process creation-time identity;
- `_windows_process_executable_path` — Windows executable-path identity;
- `_read_pid` — PID record parsing including historical PID-only compatibility;
- `is_running` — ownership-aware running-state evaluation;
- `_write_pid` — PID/creation-time/executable/installation-identity persistence;
- `_remove_pid` — PID record cleanup;
- `_kill_pid` — ownership-gated Windows task termination and non-Windows SIGKILL compatibility.

CLI command orchestration, system/network proxy mutation and network recovery deliberately remain outside this bounded slice.

## Regression contract preserved

The sealed Windows `0.2.3` process/runtime-status behaviour remains the reference contract. Slice 6 preserves:

- PAC health probe defaults (`8082`, `/proxy.pac`) and leading-slash normalization;
- loopback PAC probe request and one-second connection timeout;
- the historical 64 KiB response ceiling;
- health proof requiring `200 OK`, `FindProxyForURL` and an Arvectum localhost proxy reference;
- the distinction between a healthy compatible listener and proof that the listener belongs to this app instance;
- non-Windows `is_running` semantics based on compatible listener health;
- Windows `is_running` fail-closed ownership proof requiring a PID record, matching process creation time and matching executable path;
- PID JSON fields `pid`, `created`, `exe_path`, `identity`;
- legacy PID-only record parsing as deliberately unverified (`created=None`);
- PID write semantics using the current process, executable path and canonical install-directory identity;
- silent best-effort PID-file removal;
- refusal to call Windows `taskkill` for missing/unverified/mismatched creation time;
- the historical `taskkill /PID <pid> /F` command and no-window creation flag seam;
- non-Windows `os.kill(pid, 9)` behaviour;
- existing logging/error/fail-closed behaviour;
- dynamic monkeypatch seams for listener status, process identity helpers, PID paths, subprocess, filesystem paths and logging.

No intentional process, PID, CLI, routing, transport, recovery, backend-selection, system-proxy, release-version or packaging behaviour change was introduced.

## Canonical guard hardening

The APL-IP-003 canonical-source workflow was corrected so the explicit source boundary now includes the canonical modules introduced after the original guard was written:

- `routing_policy.py`;
- `local_proxy_transport.py`;
- `process_supervision.py`.

Its path filters and compile step now cover those modules, and the three-platform canonical matrix also executes `tests/test_process_supervision.py`. This closes the prior guard gap where the facade imported Slice 4/5 modules but direct edits to those files were not explicitly represented in the canonical-source workflow contract.

## Targeted Slice 6 coverage

`tests/test_process_supervision.py` adds direct coverage for:

- dynamic PAC-probe/settings resolution;
- structured PID record parsing;
- legacy PID-only records remaining unverified;
- listener-first fail-closed `is_running` evaluation;
- Windows executable-path mismatch rejection;
- Windows kill only after matching creation-time identity;
- non-Windows SIGKILL compatibility;
- PID cleanup through the current canonical PID path.

`tests/test_canonical_source_refactor.py` now explicitly requires `process_supervision.py` in the facade/source contract and verifies canonical ownership for all nine supervision seams.

The pre-existing `tests/test_proxy_core.py` process/PID tests were intentionally left in place. Through `import proxy_core as core` they exercised the newly installed canonical functions without being rewritten, including live PAC health, executable-path PID records, foreign-listener rejection, creation-time ownership and unsafe-taskkill refusal.

## GitHub Actions evidence

All 18 implementation PR workflow runs completed with conclusion `success` for reviewed head `deb951cdf5cf13a86c06169de33362a1ea0a1bc9` before merge.

| Gate | Run | Result |
|---|---:|---|
| APL-IP-003 canonical source | `32486989992` | SUCCESS |
| Phase 5 Config and Security | `32486989823` | SUCCESS |
| Windows P0 portable | `32486989742` | SUCCESS |
| Windows installer | `32486989887` | SUCCESS |
| APL-IP-002-WIN controlled offline build | `32486989967` | SUCCESS |
| macOS packaging | `32486989928` | SUCCESS |
| APL-LNX-008 AppImage | `32486989833` | SUCCESS |
| APL-LNX-007 Debian package | `32486989766` | SUCCESS |
| Core backend contract | `32486989725` | SUCCESS |
| APL-DIAG-004 Doctor | `32486989836` | SUCCESS |
| APL-DIAG-003/006 Windows diagnostics + privacy | `32486989811` | SUCCESS |
| APL-DIAG-001/002 structured logging + secret redaction | `32486989738` | SUCCESS |
| SAST | `32486989824` | SUCCESS |
| Secret scan | `32486989906` | SUCCESS |
| Dependency vulnerability scan | `32486989802` | SUCCESS |
| SBOM | `32486989952` | SUCCESS |
| APL-IP-001 provenance | `32486989735` | SUCCESS |
| APL-LNX-006 Linux diagnostics support bundle | `32486989932` | SUCCESS |

### Independent full-suite and package evidence

The `Phase 5 Config and Security` workflow executed the full unit suite on both Ubuntu and Windows after the extraction; both matrix jobs completed successfully. This independently exercised the historical process/PID/CLI regression tests against the canonical `process_supervision.py` seams.

The expanded APL-IP-003 canonical-source matrix completed successfully on Ubuntu, macOS and Windows, including direct compilation of the Slice 4–6 canonical modules and the new supervision tests.

Windows portable clean build/Documents smoke, Windows installer fresh/upgrade/repair/uninstall E2E and Gate R6 matrix, macOS packaging, Debian/AppImage packaging, and the controlled offline Windows build all completed successfully. The controlled offline build also proved no package-index fallback after verified CPython/wheelhouse acquisition.

## Next bounded slice

**APL-IP-003 Slice 7 — CLI / application runtime orchestration ownership extraction.**

Bounded scope: extract the command/application lifecycle currently remaining in `proxy_core_legacy.py` — local bundled-state bootstrap (`_ensure_local_files`), `_cmd_start`, `_cmd_stop`, `_cmd_rollback`, `_cmd_status`, and `main` — into a canonical runtime orchestration module. Preserve exact `0.2.3` command exit codes/messages, portable handoff-before-mutation ordering, no-upstream start guard, ProxyCore/PID/system-proxy sequencing, rollback reachability, status reporting and long-running start lifecycle. Windows network backup/registry/environment/recovery implementation remains outside Slice 7 for a later dedicated ownership extraction.

## Governance conclusion

Slice 6 is complete as an engineering refactor. It does **not** by itself declare the post-refactor source clean-IP approved and does not authorize a new clean-IP tag. The standing APL-IP-001 human/legal rights-basis gate remains required for final APL-IP-003 closure.
