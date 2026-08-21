# APL-IP-003 Slice 2 — application filesystem & portable lifecycle extraction

Date: 2026-08-21  
Status: **DONE — ACCEPTED AND MERGED**  
Protected behavioural baseline: Windows `0.2.3`  
Implementation PR: `#120`  
Merge commit: `f2507cda77ded8e21e5e3a855853d94d79ef343f`

## Purpose

Continue the bounded APL-IP-003 canonical-source migration without changing the
observable Proxy Launcher product contract. Slice 2 moves two cohesive
responsibilities out of the historical `proxy_core_legacy.py` ownership surface:

1. application filesystem and persistent/runtime state paths;
2. Windows portable executable self-heal and canonical-copy lifecycle.

The historical implementation remains in `proxy_core_legacy.py` as migration
storage during the incremental refactor, but the canonical `proxy_core` runtime
facade installs the new implementations and therefore exposes the extracted
modules as the active owners.

## Canonical ownership introduced

### `application_filesystem.py`

Owns:

- executable/source installation directory resolution;
- canonical per-user data/runtime directory resolution;
- stable Documents executable location;
- exact path comparison and temporary-root detection;
- legacy state-directory discovery;
- validated one-time state migration;
- fail-closed recovery-backup conflict recording;
- settings, recovery, quarantine, no-proxy, PID and log paths.

### `portable_lifecycle.py`

Owns:

- SHA-256 file identity checks for portable lifecycle decisions;
- canonical Documents-copy self-heal;
- owner-marker creation;
- no-fallback `managed_executable()` semantics;
- handoff only to the hash-matching canonical copy;
- canonical-install recognition.

## Compatibility contract

Slice 2 deliberately keeps the existing mutable `proxy_core` module object as
the compatibility boundary. The extracted implementations resolve collaborators
through that module object instead of taking private copies of mutable seams.

This preserves existing regression techniques such as monkeypatching:

- `core.is_windows`;
- `core.data_dir`;
- `core._legacy_state_dirs`;
- `core._STATE_READY`;
- `core.stable_app_exe`;
- `core.ensure_stable_app_copy`;
- `core._log`;
- `core.sys` / `core.os`.

`proxy_core.py` also continues to assign its own `__file__` to the legacy module
before installing the extracted filesystem layer, preserving source/frozen path
semantics established by Slice 1.

## Behaviour intentionally unchanged

- Product version remains `0.2.3`.
- No network/proxy enforcement semantics are changed.
- No routing feature is added.
- Windows portable state remains under canonical per-user storage.
- A launcher started from Downloads/TEMP is never accepted as an autostart
  fallback.
- An existing Documents executable is reused only when SHA-256 matches the
  running portable executable; otherwise it is replaced atomically.
- Ambiguous differing recovery backups continue to block migration rather than
  selecting one heuristically.
- Path-resolution failures during state migration remain fail-closed.
- Historical customer baseline/evidence is not rewritten or relabelled.

## Regression and package acceptance

`tests/test_canonical_source_refactor.py` proves:

- runtime ownership of extracted functions is the new canonical module;
- the `proxy_core` facade remains thin and explicitly wires both Slice 2 modules;
- legacy state migration still works through historical monkeypatch seams;
- path canonicalization failure during migration returns failure rather than
  continuing heuristically;
- portable self-heal replaces a mismatched canonical copy by verified hash and
  writes the install-owner marker;
- Slice 1 recovery guarantees and the frozen Windows `0.2.3` customer baseline
  remain asserted.

Accepted GitHub gates on the final PR head included:

- `APL-IP-003 canonical source` on Windows, Ubuntu and macOS;
- `Core backend contract`;
- `Phase 5 Config and Security` including the full unit suite;
- Windows canonical clean build and Documents execution smoke;
- Windows installer fresh / upgrade / repair / uninstall E2E and Gate R6 matrix;
- APL-IP-002-WIN controlled offline build;
- Debian package on Ubuntu 22.04 and 24.04;
- Linux AppImage build and inspection;
- macOS `.app` / DMG build and inspection on Apple Silicon and Intel;
- provenance, SAST, dependency vulnerability, secret, SBOM and diagnostics gates.

Platform packaging path filters were hardened so future changes to the canonical
core/extracted modules automatically trigger the relevant macOS, Debian and
AppImage package gates instead of relying only on unit-level checks.

No test or release gate was weakened for this slice.

## Closure

The bounded Slice 2 implementation was merged through PR `#120` as merge commit
`f2507cda77ded8e21e5e3a855853d94d79ef343f`. The sealed Windows `0.2.3`
release artifacts and customer baseline were not modified.

The APL-IP-001 author-to-ООО rights-basis execution reference remains a separate
**HUMAN/LEGAL PENDING** gate before any final post-refactor clean-IP candidate can
be declared APPROVED or tagged; Slice 2 completion does not waive or replace
that requirement.