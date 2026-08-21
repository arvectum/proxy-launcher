# APL-IP-003 Slice 7 — application runtime orchestration extraction evidence

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Canonical merge

- Pull request: `#130` — `APL-IP-003 Slice 7 — application runtime orchestration extraction`
- Merge commit: `c176f51e2c85185e2319a5f8669a14c9db18e50d`
- Pre-slice main baseline: `d0e8697bc07f0d72afcbd6ce04de875b6c9152a5`
- Reviewed PR head: `c26c64c0df728f52fe6ff46ad00337f7fa78c7dc`
- Product version: unchanged (`0.2.3`)
- No implementation commit was added after PR review began; no workflow rerun was required.

## Extracted ownership

`application_runtime.py` is now the canonical top-level application runtime / CLI orchestration owner, installed through the established mutable `proxy_core` compatibility seam, for:

- `_ensure_local_files` — canonical state bootstrap and frozen bundled-default copy;
- `_cmd_start` — start lifecycle orchestration;
- `_cmd_stop` — process stop plus system-proxy restore orchestration;
- `_cmd_rollback` — recovery-oriented process/network rollback orchestration;
- `_cmd_status` — CLI runtime/system-proxy/exception reporting;
- `main` — command parsing, portable handoff, bootstrap ordering and command dispatch.

Windows WinINET/registry/environment persistence, recovery Run ownership, and stale/orphan PAC recovery implementation deliberately remain outside this bounded slice.

## Behaviour contract preserved

The sealed Windows `0.2.3` command/runtime behaviour remains the reference contract. Slice 7 preserves, without intentional product change:

- no-argument invocation defaults to `start`;
- portable `--start` handoff to the canonical Documents copy occurs before state, Run-entry or network mutation;
- successful handoff prints `opened permanent launcher copy` and exits `0`;
- failed local-state bootstrap prints `state initialization failed` and exits `1` before Run-entry repair;
- Run-entry repair remains best-effort and precedes command dispatch after bootstrap;
- a missing configured upstream logs the established diagnostic, prints `upstream proxy is not configured`, exits `2`, and does not instantiate/start the proxy or mutate system proxy state;
- an already-running owned process reuses the established `enable_system_proxy()` path and returns `0`/`1` from that result;
- new start ordering remains `ProxyCore.start()` -> PID write -> system-proxy enable;
- proxy start failure keeps the established log/print path and exits `1`;
- system-proxy enable failure stops the local proxy, removes the PID record, prints the established rollback message and exits `1`;
- successful start keeps the long-running `Event.wait(3600)` lifecycle, accepts `KeyboardInterrupt`, and always stops the local proxy/removes the PID record in `finally`;
- stop and rollback retain safe PID termination followed by network disable/restore evaluation;
- incomplete network restore remains a non-zero outcome and keeps recovery files for retry;
- status output retains the established RUNNING/STOPPED, system-proxy and exception-count messages;
- unknown/invalid CLI forms retain the established usage text and exit `2`.

## Compatibility boundary

All lower-level collaborators are resolved dynamically from the same mutable `proxy_core` module object. This preserves the established monkeypatch seams while using the canonical owners already installed for filesystem, configuration, routing, local transport, process supervision and cross-platform system-proxy composition.

`proxy_core_legacy.py` was not edited in this slice. Historical source remains truthful evidence while executable ownership moves to the canonical module.

## Targeted regression coverage

`tests/test_application_runtime.py` adds bounded checks for:

- Slice 7 source ownership;
- bundled-default bootstrap after canonical state readiness;
- portable handoff-before-mutation ordering;
- state-bootstrap failure before Run-entry repair;
- no-upstream fail-fast before process/network mutation;
- cleanup after system-proxy enable failure;
- cleanup after long-running start interruption;
- stop incomplete-network-restore behaviour;
- rollback reachability without a PID record;
- status reporting through canonical runtime seams.

The APL-IP-003 canonical-source workflow was extended to compile `application_runtime.py` and run its targeted tests with the existing canonical refactor suites on Ubuntu, macOS and Windows.

## Independent full-suite evidence

The pre-existing full unit suite was not rewritten around the extraction. `Phase 5 Config and Security` completed successfully on Ubuntu and Windows and therefore independently exercised existing CLI/process/recovery tests through the installed `proxy_core` facade, including the prior `_cmd_stop` and `_cmd_rollback` incomplete-recovery regressions.

## Implementation PR workflow evidence — 18/18 SUCCESS

- `32488659464` — APL-DIAG-003/006 Windows diagnostics + privacy
- `32488659517` — SBOM
- `32488659484` — APL-LNX-006 Linux diagnostics support bundle
- `32488659503` — macOS packaging
- `32488659547` — Core backend contract
- `32488659559` — Dependency vulnerability scan
- `32488659563` — APL-DIAG-001/002 structured logging + secret redaction
- `32488659446` — Phase 5 Config and Security
- `32488659610` — APL-IP-003 canonical source
- `32488659661` — Windows installer
- `32488659667` — APL-LNX-008 AppImage
- `32488659625` — APL-IP-001 provenance
- `32488659590` — APL-IP-002-WIN controlled offline build
- `32488659467` — APL-LNX-007 Debian package
- `32488659671` — SAST
- `32488659532` — APL-DIAG-004 Doctor
- `32488659588` — Windows P0 portable
- `32488659633` — Secret scan

## Release / packaging evidence

- Canonical-source compile + targeted regression: Ubuntu, macOS and Windows — SUCCESS.
- Full unit suite: Ubuntu and Windows — SUCCESS.
- Windows P0 portable: canonical clean build + Documents execution smoke — SUCCESS.
- Windows installer: pinned Inno Setup / sovereignty checks, portable baseline, predecessor fixture, canonical installer compile, fresh/upgrade/repair/uninstall E2E and Gate R6 — SUCCESS.
- Controlled offline Windows build: Sigstore-verified CPython base, exact CPython 3.12 wheelhouse, offline archive verification, offline canonical portable build and explicit no-package-index-fallback proof — SUCCESS.
- macOS package, Debian package and AppImage package gates — SUCCESS.
- SAST, dependency vulnerability, secret scan, provenance, SBOM, diagnostics and backend-contract gates — SUCCESS.

## Governance

This is an engineering ownership/refactor completion only. It does not declare the repository clean-IP APPROVED and does not authorize a clean-IP tag. The APL-IP-001 author-to-ООО rights-basis execution remains HUMAN/LEGAL PENDING and must be reconciled during the post-refactor IP baseline process.

Git history and AI/automation provenance have not been rewritten or reassigned.

## Next bounded slice

**APL-IP-003 Slice 8 — Windows WinINET / proxy-environment persistence and system-proxy implementation ownership extraction.**

Planned bounded ownership: PAC URL/state helpers, Internet Settings snapshot/restore validation, registry mutation primitives, user proxy-environment snapshot/restore/synchronization, WinINET refresh, and the Windows implementations consumed by `system_proxy_runtime` for enable/disable/status/restore-pending.

Recovery Run/autostart ownership/classification and stale/orphan PAC diagnostic/cleanup remain separate later slices so ownership-sensitive recovery behaviour can be reviewed independently.
