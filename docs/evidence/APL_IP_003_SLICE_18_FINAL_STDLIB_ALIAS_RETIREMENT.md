# APL-IP-003 Slice 18 — socket compatibility-seam replacement & final stdlib-alias retirement

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Purpose

Retire the final standard-library compatibility alias from the mutable `proxy_core` namespace after moving every supported internal socket monkeypatch to the canonical module that owns the corresponding behavior.

The slice preserves the sealed Windows `0.2.3` behavior contract and deliberately leaves the `sys.modules[__name__] = _core` module-identity boundary unchanged for a later independent compatibility decision.

## Baseline and merge

- pre-slice protected `main`: `ef41d111b144eb8a4ea02f58f291162f872b710b`
- implementation PR: `#152`
- final reviewed implementation head: `af1c235a61f7e5d31556e92d6a344763bd0b0203`
- implementation merge: `860343d2dce76a3e30efd7f76385550a5e3137cd`
- product version: `0.2.3` unchanged

## Final compatibility-alias result

Slice 17 entered Slice 18 with exactly one compatibility-only stdlib alias in `proxy_core_legacy.py`:

- `socket`

Slice 18 physically removes that final import. The mutable core compatibility shell therefore reaches:

- **stdlib compatibility aliases: 1 -> 0 in this slice**;
- **Slice 15 guarded stdlib inventory: 10 -> 0 across Slices 16-18**;
- **all 13 historically tracked `core.<stdlib>` names retired** when earlier Slice 13 retirements are included.

`proxy_core_legacy.py` now has no ordinary stdlib imports and still contains no runtime function, class, or lambda implementation. Its remaining purpose is bounded pre-composition release/state/install identity while `proxy_core.py` composes canonical owners onto the established mutable module object.

## Socket seam migration

No maintained runtime implementation used `core.socket` before this slice. The remaining dependency existed only because regression tests patched the shared stdlib module through the historical facade alias.

Slice 18 moves those injection points to the canonical owners without changing the operations under test:

- `tests/test_network_change.py`
  - listener/socket factory, DNS lookup, direct-connect and upstream-connect patches -> `local_proxy_transport.socket`;
  - PAC health-probe connection patch -> `process_supervision.socket`.
- `tests/test_local_proxy_transport.py`
  - direct HTTP transport connection patch -> `local_proxy_transport.socket`.
- `tests/test_proxy_core.py`
  - direct excluded HTTP, CONNECT and SOCKS connection patches -> `local_proxy_transport.socket`.

The public/runtime calls remain the same composed `proxy_core` functions and classes. Only the regression dependency-injection target moved from a historical compatibility alias to the module that owns the socket behavior.

## Guard caught residual consumers before merge

The first zero-alias implementation attempt intentionally strengthened the repository-wide guard before assuming the migration was complete. Canonical-source CI then failed its consumer assertion and identified two remaining test-only consumers:

- `tests/test_local_proxy_transport.py`
- `tests/test_proxy_core.py`

Those exact residual seams were migrated to `local_proxy_transport.socket`. The final implementation head then passed the same repository-wide guard on Windows, macOS, and Ubuntu.

This failed-first-guard event is retained as positive engineering evidence: the zero-consumer claim was not inferred from a narrow search and the implementation could not merge until the AST inventory proved the consumer map empty.

## Guard strengthening

`tests/test_legacy_compatibility_shell.py` now enforces the following repository-wide invariants:

1. all 13 historically tracked stdlib aliases are absent from the live `proxy_core` namespace;
2. the retired set equals the complete historical stdlib-alias inventory;
3. `proxy_core_legacy.py` has zero plain imports and therefore zero stdlib compatibility imports;
4. the repository-wide AST consumer map for historical `core.<stdlib>` attributes is empty;
5. `local_proxy_transport.py` and `process_supervision.py` own `socket` locally and do not resolve it through core;
6. every canonical runtime owner remains free of historical `core.<stdlib>` service-location;
7. the compatibility/state shell contains no runtime function/class/lambda implementation;
8. every live project runtime callable still has an explicit canonical owner;
9. the established `proxy_core` / `proxy_core_legacy` mutable module-object identity remains explicitly tested and unchanged in this slice.

## Final implementation CI evidence

Final reviewed head `af1c235a61f7e5d31556e92d6a344763bd0b0203` completed **14/14 triggered workflows successfully**.

Key evidence:

- APL-IP-003 canonical source — Ubuntu/macOS/Windows matrix: success;
- Windows P0 portable: success;
- Windows canonical clean build — **625 tests, all passed**;
- Windows Documents execution smoke: success;
- packaged Doctor smoke: success;
- Windows installer — pinned Inno Setup validation, portable baseline, synthetic predecessor fixture, canonical installer compile, fresh/upgrade/repair/uninstall E2E and Gate R6: success;
- APL-IP-002-WIN controlled offline build — Sigstore-verified CPython, exact Windows wheelhouse, offline archive verification, canonical offline portable build and no-package-index-fallback proof: success;
- macOS packaging — Apple Silicon and Intel: success;
- Debian package: success;
- AppImage: success;
- Linux diagnostics/support bundle: success;
- Core backend contract: success;
- SAST: success;
- Secret scan: success;
- dependency vulnerability scan: success;
- SBOM: success;
- APL-IP-001 provenance: success.

The Windows clean-build suite explicitly executed the migrated network-change, local-transport and monolithic proxy-core regressions after `core.socket` had been physically removed. The zero-import and empty-consumer AST guards also passed in that same packaged-build path.

The test count changed from the Slice 17 Windows result of 626 to 625 because the retained-socket compatibility identity assertion was replaced by the final zero-alias invariants; no product behavior regression test was removed.

## Behavioral and governance result

- sealed Windows `0.2.3` behavior remains the reference contract;
- no canonical runtime owner implementation changed in this slice;
- no user-visible feature was added or removed;
- no listener, DNS, PAC, direct/upstream transport, process-supervision, recovery or system-proxy behavior changed;
- no Git history or provenance evidence was rewritten;
- stdlib compatibility-alias inventory is now zero;
- ordinary stdlib service-location through mutable core is eliminated;
- `sys.modules[__name__] = _core` remains unchanged and is not implicitly approved for removal merely because the stdlib alias inventory reached zero;
- engineering completion does **not** constitute clean-IP approval;
- the author-to-ООО rights-basis and final post-refactor human/legal review remain mandatory before any clean-IP candidate can be APPROVED or tagged.

## Next bounded slice

**APL-IP-003 Slice 19 — compatibility module-identity boundary inventory & retirement feasibility.**

Inventory every behavior and test that depends on `import proxy_core` returning the same mutable module object as `proxy_core_legacy`, classify which dependencies are genuine sealed compatibility contracts versus historical test/construction artifacts, and define the smallest safe retirement path. Remove or redesign `sys.modules[__name__] = _core` only if repository-wide and cross-platform evidence proves behavior equivalence; otherwise retain the boundary with an explicit justification and move to the next canonicalization target.
