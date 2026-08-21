# APL-IP-003 Slice 15 — platform/recovery dependency namespace decoupling & compatibility-alias inventory

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Purpose

Finish the bounded canonical-owner migration away from using the mutable `proxy_core` module as a generic standard-library service locator in the remaining application/recovery runtime layer, while making the residual stdlib compatibility namespace explicit and machine-checked.

The slice preserves the sealed Windows `0.2.3` behavior contract, historical monkeypatch compatibility, fail-closed Recovery Run ownership semantics, and the existing `sys.modules` module-identity boundary.

## Baseline and merge

- pre-slice protected `main`: `2b1f5b135916fe73cb5cfac85b5c68c931b9c957`
- implementation PR: `#146`
- final reviewed implementation head: `7462008472232cb91d28cefe1c3a13cb21980692`
- implementation merge: `13fe2cb048054df41d43e9509f61d821ea86bc3c`
- product version: `0.2.3` unchanged

## Inventory result

The platform/recovery/application-runtime review found:

- `windows_system_proxy.py` already owns ordinary `io`, `json`, `os`, and URL parsing locally;
- `windows_pac_recovery.py` already owns ordinary `io`, `json`, `os`, and `time` locally;
- `system_proxy_runtime.py` does not resolve ordinary stdlib dependencies through mutable core;
- `logging_bridge.py` uses the core seam only for behavior-sensitive logger/path/version collaborators;
- the remaining service-locator use in the Slice-15 target area was concentrated in `application_runtime.py` and `recovery_autostart.py`.

## Bounded source changes

### `application_runtime.py`

The module now owns ordinary dependencies locally:

- `os`
- `shutil`
- `sys`

The implementation no longer performs `core.os` or `core.sys` lookup. The mutable core seam remains for actual application/runtime collaborators such as state initialization, path ownership, handoff, process supervision, system-proxy operations, routing policy, logging and CLI subcommand functions.

### `recovery_autostart.py`

The module already owned `os` and `re`. Slice 15 adds local ownership of:

- `subprocess`
- `sys`

The implementation no longer performs `core.subprocess` or `core.sys` lookup. Recovery ownership/classification, managed-executable resolution, exact Run mutation, logging, path classification and Windows capability checks remain dynamically resolved through core because those are behavior-sensitive compatibility collaborators rather than generic stdlib dependencies.

## Compatibility-alias inventory

The residual `proxy_core_legacy.py` stdlib imports are now an explicit compatibility-only set:

- `base64`
- `hashlib`
- `io`
- `json`
- `os`
- `socket`
- `subprocess`
- `sys`
- `threading`
- `time`

The guard requires the shell import set to equal this inventory exactly.

No alias was physically removed in Slice 15 because supported regression tests still patch several of these module objects through the historical `core` surface. Previous Slice 13 evidence already established `socket` as a real compatibility seam. Slice 14 and Slice 15 further prove that local imports and retained aliases resolve to the same Python module objects, so monkeypatches remain effective without maintained implementations looking dependencies up through core.

This is intentional shell minimization discipline: an alias is removed only after repository-wide evidence proves that neither maintained runtime owners nor supported compatibility tests require it.

## Guard changes

`tests/test_legacy_compatibility_shell.py` now additionally proves:

1. `application_runtime.py` has no exact `core.os` or `core.sys` access;
2. `recovery_autostart.py` has no exact `core.subprocess` or `core.sys` access;
3. the retained compatibility import set in `proxy_core_legacy.py` exactly equals the governed alias inventory;
4. `core.os is application_runtime.os`;
5. `core.sys is application_runtime.sys`;
6. `core.sys is recovery_autostart.sys`;
7. `core.subprocess is recovery_autostart.subprocess`;
8. all Slice 12–14 no-runtime-implementation, explicit-callable-owner, removed-alias and decoupled-owner guards remain active.

## Final implementation CI evidence

Final reviewed head `7462008472232cb91d28cefe1c3a13cb21980692` completed every workflow triggered by this bounded path set: **8/8 SUCCESS**.

- APL-IP-003 canonical source — Ubuntu/macOS/Windows matrix success
- Windows P0 portable — success, including canonical Windows clean build and Documents execution smoke
- Windows installer — success, including pinned Inno Setup, portable baseline, synthetic predecessor lifecycle fixture, canonical installer compile, fresh/upgrade/repair/uninstall E2E and Gate R6 acceptance
- SAST — success
- Secret scan — success
- Dependency vulnerability scan — success
- SBOM — success
- APL-IP-001 provenance — success

The Windows clean-build result is the key compatibility proof for this slice: historical tests that patch shared stdlib module objects through `core.sys`, `core.subprocess`, and related compatibility aliases continue to affect the locally imported module objects used by maintained runtime code.

## Behavioral and governance result

- sealed Windows `0.2.3` behavior remains the reference contract;
- no product feature was added or removed;
- Recovery Run ownership and foreign-entry preservation remain fail-closed;
- no network mutation behavior was changed;
- no Git history or provenance evidence was rewritten;
- retained stdlib names are now explicitly classified as compatibility aliases rather than architectural dependencies;
- `sys.modules[__name__] = _core` remains unchanged;
- engineering completion does **not** constitute clean-IP approval;
- the author-to-ООО rights-basis and final post-refactor human/legal review remain required before any clean-IP candidate can be APPROVED or tagged.

## Next bounded slice

**APL-IP-003 Slice 16 — compatibility-alias retirement & shell minimization.**

Build a precise supported-consumer map for each retained stdlib alias, migrate internal regression tests from broad `core.<stdlib>` patching to canonical-owner or narrow explicit behavior seams where this does not weaken the compatibility contract, and physically remove only aliases proven unused after that migration. The `sys.modules` module-identity boundary remains a separate later slice and must not be removed merely as a side effect of alias cleanup.
