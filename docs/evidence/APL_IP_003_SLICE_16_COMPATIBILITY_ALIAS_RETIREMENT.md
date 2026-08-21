# APL-IP-003 Slice 16 — compatibility-alias retirement & shell minimization

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Purpose

Reduce the residual `proxy_core_legacy.py` compatibility namespace only where repository-wide evidence proves an alias is no longer required, while preserving the sealed Windows `0.2.3` behavior contract and the established mutable compatibility boundaries that still have supported regression consumers.

This slice deliberately does not remove the `sys.modules[__name__] = _core` module-identity boundary. Module-identity retirement remains a separate later decision and must be proven independently.

## Baseline and merge

- pre-slice protected `main`: `35733db08215a098a85d3e2c93b8496bb7e2f221`
- implementation PR: `#148`
- final reviewed implementation head: `6f887cae34c34e95c7f7c9376388b49ec9fee379`
- implementation merge: `bd3804471ec205c9da251150461d7dd273d96003`
- product version: `0.2.3` unchanged

## Compatibility-alias retirement result

Slice 15 entered with ten compatibility-only stdlib aliases in `proxy_core_legacy.py`:

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

Slice 16 physically removes six aliases whose remaining internal consumers were eliminated or proven absent:

- `base64`
- `hashlib`
- `io`
- `json`
- `threading`
- `time`

The compatibility shell therefore shrinks from **10 stdlib aliases to 4**.

The retained aliases are exactly:

- `os` — legacy-regression-only compatibility consumer class;
- `socket` — established shared monkeypatch compatibility seam used by transport/network regression tests;
- `subprocess` — legacy-regression-only compatibility consumer class;
- `sys` — legacy-regression-only compatibility consumer class.

No maintained canonical runtime owner resolves ordinary stdlib dependencies through these retained names.

Historical aliases `re`, `select`, and `struct`, removed in earlier slices, remain part of the machine-checked historical inventory so accidental reintroduction is also rejected.

## Internal regression migration

To reduce false compatibility dependencies without altering product behavior, Slice 16 moves internal patching to the actual canonical owner where safe:

- configuration atomic-write/I/O fault injection now patches `configuration_storage.os` / `configuration_storage.io`;
- application-runtime frozen/argv seams now patch `application_runtime.sys`;
- process-supervision process/kill seams now patch `process_supervision.subprocess` / `process_supervision.os`;
- canonical-source filesystem path-resolution fault injection now patches `application_filesystem.os.path`;
- portable self-heal frozen/executable seams now patch `portable_lifecycle.sys`;
- network-change thread creation now patches `local_proxy_transport.threading`.

`core.socket` patching is intentionally preserved because it is already an established shared mutable compatibility seam and its removal is not proven safe in this slice.

## Repository-wide guard

`tests/test_legacy_compatibility_shell.py` now includes an AST-based consumer guard over the repository Python source tree.

The guard proves that:

1. retired stdlib aliases are absent from the live `proxy_core` namespace;
2. `proxy_core_legacy.py` imports exactly the four retained compatibility aliases;
3. no live project Python consumer accesses any retired historical `proxy_core.<stdlib>` alias;
4. every live consumer of a retained alias is bounded to regression tests rather than maintained runtime owners;
5. `core.socket` remains the same Python module object used by `local_proxy_transport` and `process_supervision`;
6. every maintained canonical owner remains free of historical `core.<stdlib>` service-location;
7. `proxy_core_legacy.py` still contains no runtime function/class/lambda implementation;
8. every live project runtime callable still has an explicit canonical owner.

This converts compatibility-alias retirement from an informal cleanup preference into a regression-protected architectural invariant.

## Final implementation CI evidence

Final reviewed head `6f887cae34c34e95c7f7c9376388b49ec9fee379` completed **15/15 triggered workflows successfully**.

Key compatibility and regression evidence:

- APL-IP-003 canonical source — Ubuntu/macOS/Windows matrix: success;
- Phase 5 Config and Security — Windows/Ubuntu contract tests and full unit suites: success;
- Windows P0 portable — canonical clean build and Documents execution smoke: success;
- Windows installer — pinned Inno Setup, canonical installer build, lifecycle E2E and Gate R6 acceptance: success;
- APL-IP-002-WIN controlled offline build — verified CPython/wheelhouse offline canonical portable build and no-index-fallback proof: success;
- Core backend contract: success;
- macOS packaging: success;
- Debian package: success;
- AppImage: success;
- Linux diagnostics/support bundle: success;
- SAST: success;
- Secret scan: success;
- Dependency vulnerability scan: success;
- SBOM: success;
- APL-IP-001 provenance: success.

The cross-platform canonical-source matrix plus Windows/Ubuntu full-unit-suite results are the primary evidence that removing six compatibility aliases did not alter the supported runtime/test contract.

## Behavioral and governance result

- sealed Windows `0.2.3` behavior remains the reference contract;
- no user-visible product feature was added or removed;
- no network mutation/recovery semantics were changed;
- no Git history or provenance evidence was rewritten;
- compatibility shell stdlib surface is reduced by 60%, from 10 aliases to 4;
- the remaining four aliases are explicit, classified, consumer-bounded compatibility debt rather than architectural dependencies;
- `sys.modules[__name__] = _core` remains unchanged;
- engineering completion does **not** constitute clean-IP approval;
- the author-to-ООО rights-basis and final post-refactor human/legal review remain required before any clean-IP candidate can be APPROVED or tagged.

## Next bounded slice

**APL-IP-003 Slice 17 — remaining legacy regression seam retirement.**

Migrate the remaining regression-only `core.os`, `core.subprocess`, and `core.sys` consumers—primarily the broad legacy `test_proxy_core` surface and any residual recovery tests—to canonical-owner or narrower explicit behavior seams, then physically remove only aliases proven unused by the repository-wide guard. Keep `core.socket` until its established shared monkeypatch contract is independently replaced or proven unnecessary. Removal of the `sys.modules` module-identity boundary remains a later independent slice after compatibility-alias retirement is complete.
