# APL-IP-003 Slice 11 — structured logging bridge ownership extraction evidence

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Canonical merge

- Pull request: `#138` — `APL-IP-003 Slice 11 — structured logging bridge extraction`
- Merge commit: `282581aab129db57f81751ba62420a26f2060f8a`
- Pre-slice main baseline: `32e5388c0bfa6bee9cf6fd8d0c5fccee191b2814`
- Reviewed final PR head: `e0920c2ced94568a8c0548584d12662d3811800e`
- Product version: unchanged (`0.2.3`)
- Final implementation diff changed exactly four files: `.github/workflows/apl-ip-003-canonical-source.yml`, `logging_bridge.py`, `proxy_core.py`, and `tests/test_logging_bridge.py`.
- `proxy_core_legacy.py` was not edited.

## Extracted ownership

`logging_bridge.py` is now the canonical owner for the proxy-core logging bridge:

- construction of the `StructuredLogger` singleton exposed as `core.structured_logger`;
- `structured_log(message, level=None, event=None, **fields)`;
- `_log(msg)` compatibility sink used throughout the historical/core call surface.

The lower-level JSONL schema, event/level derivation, secret redaction, legacy-log preservation, bounded rotation, and best-effort write implementation remain owned by the existing `structured_logging.py` diagnostics module. Slice 11 does not duplicate or fork that implementation.

## Preserved compatibility contract

The exact sealed `0.2.3` bridge semantics remain intact:

1. the logger is constructed with `APP_VERSION`, `ENGINEERING_MILESTONE`, and component `proxy_core`;
2. the path getter resolves `core.log_path()` dynamically, so the canonical filesystem owner and historical monkeypatch seam remain authoritative;
3. `structured_log()` resolves `core.structured_logger` at call time rather than capturing a private immutable reference;
4. `_log()` resolves `core.structured_log` at call time, preserving the established mutable test/caller seam;
5. empty structured fields remain `None` rather than an empty mapping;
6. logger I/O/path/encoding/rotation failures remain swallowed by `StructuredLogger.log()` and cannot interrupt start/stop/rollback/recovery logic;
7. no logging format, event mapping, redaction rule, rotation limit, log location, product version, or milestone was changed by this slice.

The canonical bridge is installed immediately after `application_filesystem`, before other extracted runtime owners. Therefore the singleton path getter observes the canonical `log_path()` while all later owners see the canonical `_log` bridge.

## Targeted regression coverage

`tests/test_logging_bridge.py` proves:

- `structured_log` and `_log` are owned by `logging_bridge`;
- the installed singleton is a `StructuredLogger` with exact app-version/milestone/component metadata;
- `log_path` remains dynamically monkeypatchable after singleton construction;
- a normal `_log` record retains the structured schema/event/product metadata;
- `structured_log` dynamically honors a patched `core.structured_logger`;
- `_log` dynamically honors a patched `core.structured_log`;
- the historical `fields=None` call contract remains unchanged;
- a real invalid log path still returns `None` rather than raising.

The canonical-source workflow was also expanded to compile and run both `tests/test_logging_bridge.py` and the pre-existing `tests/test_structured_logging.py`, preventing the extraction from being validated only by newly written tests.

## Implementation workflow evidence

All 18 pull-request workflows for reviewed head `e0920c2ced94568a8c0548584d12662d3811800e` completed successfully:

- `32497894907` — APL-IP-001 provenance — SUCCESS
- `32497894924` — SAST — SUCCESS
- `32497894961` — APL-DIAG-003/006 Windows diagnostics + privacy — SUCCESS
- `32497894911` — APL-LNX-007 Debian package — SUCCESS
- `32497894922` — Core backend contract — SUCCESS
- `32497895038` — APL-DIAG-001/002 structured logging + secret redaction — SUCCESS
- `32497895073` — macOS packaging — SUCCESS
- `32497895027` — APL-DIAG-004 Doctor — SUCCESS
- `32497895003` — APL-LNX-008 AppImage — SUCCESS
- `32497895096` — APL-LNX-006 Linux diagnostics support bundle — SUCCESS
- `32497895145` — Phase 5 Config and Security — SUCCESS
- `32497895125` — Windows installer — SUCCESS
- `32497895172` — SBOM — SUCCESS
- `32497895168` — Secret scan — SUCCESS
- `32497895180` — APL-IP-003 canonical source — SUCCESS
- `32497895182` — Windows P0 portable — SUCCESS
- `32497895183` — APL-IP-002-WIN controlled offline build — SUCCESS
- `32497895205` — Dependency vulnerability scan — SUCCESS

High-value independent evidence:

- APL-IP-003 canonical-source regression passed on Ubuntu, macOS, and Windows and included both the new logging-bridge suite and existing structured-logging suite.
- The dedicated logging/redaction workflow passed structured logging tests, secret-redaction tests, and the full unit suite on both Windows and Ubuntu.
- Phase 5 ran its full unit suite successfully on both Windows and Ubuntu, independently exercising existing call sites that use `_log` across configuration, recovery, transport, and runtime orchestration.
- Windows P0 portable clean build and Documents execution smoke passed.
- Windows installer fresh/upgrade/repair/uninstall E2E and Gate R6 acceptance matrix passed.
- Controlled offline build passed official CPython Sigstore verification, exact wheelhouse acquisition, offline canonical portable build, and no-package-index-fallback proof.

## Governance

Slice 11 is an engineering ownership/refactor milestone only. It does not assert that the repository is legally clean-IP approved, does not rewrite or relabel historical authorship, and does not satisfy the still-pending human/legal author-to-ООО rights-basis gate.

The sealed Windows `0.2.3` customer-confirmed baseline remains unchanged.

## Next bounded slice

**APL-IP-003 Slice 12 — `proxy_core_legacy` compatibility-shell reduction & live callable inventory.**

The slice should first establish an explicit runtime callable-owner inventory/guard, identify any remaining live callable still owned by `proxy_core_legacy`, move any such bounded residue to its correct canonical owner, and only after that evidence is green reduce the historical module to the compatibility/state/import surface still required by the mutable facade. Removal of the `sys.modules` compatibility boundary itself is deliberately out of scope for Slice 12 unless an independent proof shows it is no longer required.
