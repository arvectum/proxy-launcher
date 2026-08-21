# APL-IP-003 Slice 17 — remaining legacy regression seam retirement

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Purpose

Retire the remaining regression-only `proxy_core` standard-library compatibility aliases after moving supported internal monkeypatch seams to the canonical modules that actually own the corresponding runtime behavior.

The slice preserves the sealed Windows `0.2.3` behavior contract, keeps the established shared `core.socket` monkeypatch seam intact, and deliberately leaves the `sys.modules[__name__] = _core` module-identity boundary for a later independent decision.

## Baseline and merge

- pre-slice protected `main`: `2fb676fb95e480f18882fdef2b770df4692283c0`
- implementation PR: `#150`
- final reviewed implementation head: `dac12a656f05bb8d877d6d99295d60c9c2f0446a`
- implementation merge: `6d0d6efb1bb8497fa159fa74db0ae3c111ba27d4`
- product version: `0.2.3` unchanged

## Compatibility-alias retirement result

Slice 16 entered Slice 17 with four compatibility-only stdlib aliases in `proxy_core_legacy.py`:

- `os`
- `socket`
- `subprocess`
- `sys`

Slice 17 physically removes the three aliases that were retained only for legacy regression patching:

- `os`
- `subprocess`
- `sys`

The compatibility shell therefore shrinks from **4 stdlib aliases to 1**.

The sole retained stdlib alias is:

- `socket` — an established shared monkeypatch compatibility seam used by network/transport regression tests.

No maintained canonical runtime owner resolves ordinary stdlib dependencies through the mutable `proxy_core` namespace.

## Regression-seam migration

The old monolithic `tests/test_proxy_core.py` suite still exercised valid sealed behavior, but several tests patched stdlib modules through historical `core.<stdlib>` names. Slice 17 keeps the behavior assertions while moving those patches to the actual canonical owners:

- state/data-path environment and path behavior → `application_filesystem.os`;
- portable frozen/executable and handoff process behavior → `portable_lifecycle.sys` / `portable_lifecycle.subprocess`;
- PID identity and kill behavior → `process_supervision.sys` / `process_supervision.os` / `process_supervision.subprocess`;
- Windows backup-file existence/removal behavior → `windows_system_proxy.os`;
- legacy recovery process inspection → `recovery_autostart.subprocess`.

The tested public/runtime operations continue to be invoked through the same composed `proxy_core` functions. Only the test injection point moved from a historical service-locator alias to the canonical module that owns the dependency.

## Guard strengthening

`tests/test_legacy_compatibility_shell.py` now enforces the following repository-wide invariants:

1. every historical stdlib alias except `socket` is retired from the live `proxy_core` namespace;
2. `proxy_core_legacy.py` imports exactly one stdlib module: `socket`;
3. no live project Python consumer accesses any retired `core.<stdlib>` alias, including `core.os`, `core.subprocess`, or `core.sys`;
4. the only remaining live compatibility-alias consumer class is `core.socket` in regression tests;
5. `core.socket` is still the same Python module object used by `local_proxy_transport` and `process_supervision`;
6. canonical runtime owners remain free of historical `core.<stdlib>` service-location;
7. `proxy_core_legacy.py` still contains no runtime function/class/lambda implementation;
8. every live project runtime callable still has an explicit canonical owner.

Repository search also found no `from proxy_core import ...` form that could bypass the attribute-based compatibility consumer inventory.

## Final implementation CI evidence

Final reviewed head `dac12a656f05bb8d877d6d99295d60c9c2f0446a` completed **14/14 triggered workflows successfully**.

Key evidence:

- APL-IP-003 canonical source — Ubuntu/macOS/Windows matrix: success;
- Windows P0 portable — success;
- Windows canonical clean build — **626 tests, all passed**;
- Windows Documents execution smoke — success;
- packaged Doctor smoke — success;
- Windows installer — pinned Inno Setup validation, portable baseline, synthetic predecessor fixture, canonical installer compile, fresh/upgrade/repair/uninstall E2E and Gate R6: success;
- APL-IP-002-WIN controlled offline build — verified CPython acquisition, exact wheelhouse, offline archive verification, canonical offline portable build and no-package-index-fallback proof: success;
- macOS packaging — Apple Silicon and Intel tests/build/.app/DMG inspection: success;
- Debian package: success;
- AppImage: success;
- Linux diagnostics/support bundle: success;
- Core backend contract: success;
- SAST: success;
- Secret scan: success;
- Dependency vulnerability scan: success;
- SBOM: success;
- APL-IP-001 provenance: success.

The Windows clean-build suite explicitly executed the migrated `test_proxy_core` and `test_recovery_autostart` cases after `core.os`, `core.subprocess`, and `core.sys` had been physically removed. The new `test_only_socket_remains_as_live_compatibility_alias_consumer` and retired-alias repository scan also passed.

## Behavioral and governance result

- sealed Windows `0.2.3` behavior remains the reference contract;
- no maintained runtime implementation was changed in this slice;
- no user-visible product feature was added or removed;
- no network mutation, recovery ownership, proxy restore or process safety semantics were changed;
- no Git history or provenance evidence was rewritten;
- stdlib compatibility surface is reduced by 75% within this slice, from four aliases to one;
- across the Slice 15 inventory, the shell has now fallen from ten stdlib aliases to one;
- `socket` remains explicit compatibility debt, not an architectural dependency;
- `sys.modules[__name__] = _core` remains unchanged;
- engineering completion does **not** constitute clean-IP approval;
- the author-to-ООО rights-basis and final post-refactor human/legal review remain mandatory before any clean-IP candidate can be APPROVED or tagged.

## Next bounded slice

**APL-IP-003 Slice 18 — socket compatibility-seam replacement & final stdlib-alias retirement.**

Independently map every supported `core.socket` consumer and replace broad shared-module patching with canonical-owner or narrower explicit network behavior seams only where the sealed transport/network-change contract remains equivalent. Physically remove `socket` from `proxy_core_legacy.py` only after repository-wide and cross-platform evidence proves the compatibility surface no longer requires it.

Removal or redesign of the `sys.modules` module-identity boundary remains a separate later slice even if Slice 18 reaches zero stdlib compatibility aliases.