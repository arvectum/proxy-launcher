# APL-IP-003 Slice 21 — regression naming & repository hygiene

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-22

## Scope

Slice 21 removed refactor-task numbering from maintained regression-test API names and established a permanent repository-identity hygiene guard. It did not change production runtime behavior, network/recovery semantics, packaging semantics, or the sealed `0.2.3` product baseline.

## Baseline

Protected `main` before the Slice 21 implementation was the Slice 20 closure merge:

- `5fd4cfe13aaefea89ff2b002e99ae3d36f090cf4`

## Authoritative inventory

The first repository-hygiene guard run was intentionally used as an inventory probe. It found exactly 15 maintained test function/method names containing historical `sliceN` task numbering across six files:

- `tests/test_application_runtime.py` — 1;
- `tests/test_canonical_source_refactor.py` — 9;
- `tests/test_logging_bridge.py` — 1;
- `tests/test_recovery_autostart.py` — 1;
- `tests/test_windows_pac_recovery.py` — 1;
- `tests/test_windows_system_proxy.py` — 2.

No production callable depended on those names. Only the Python test identifiers were renamed; test bodies and assertions were intentionally preserved.

The repository-identity probe also confirmed that no real maintained file still depended on the former repository slug. The only initial matches were the bounded normalization workflow itself and the guard's own literal. The permanent guard constructs the historical slug without embedding it verbatim in maintained current-tree text.

## Permanent invariants

`tests/test_repository_hygiene.py` now enforces:

1. no maintained `test_*` function or method name may contain `slice\d+`;
2. current maintained files use `arvectum/proxy-launcher` rather than the former repository identity;
3. `.mailmap`, historical evidence under `docs/evidence/`, and release baselines under `release/baselines/` remain explicit historical exceptions;
4. `.mailmap` continues to preserve the historical `arutyunoveth` human identity mapping without rewriting Git history;
5. current governance contains the canonical `arvectum/proxy-launcher` repository identity.

The guard is compiled and executed in the cross-platform APL-IP-003 canonical-source workflow.

## First implementation PR and protected-branch evidence

The initial implementation was developed in PR #158 (`apl-ip-003-slice-21-test-repository-hygiene`). Final head:

- `9deed442f2bd918fdd57e5229212077b50985948`

That head completed all 9 triggered workflows successfully, including:

- APL-IP-003 canonical source on Windows, macOS and Ubuntu;
- Core backend contract;
- APL-IP-001 provenance;
- SAST;
- Dependency vulnerability scan;
- SBOM;
- Secret scan;
- Windows P0 portable clean build and Documents execution smoke;
- Windows installer lifecycle E2E and Gate R6.

GitHub branch protection nevertheless kept the required `build` context in `expected` state for the merge because the feature branch ancestry predated the latest protected-main closure merge. The protection rule was not bypassed. No force-push, history rewrite, or artificial status manipulation was used.

PR #158 was closed as superseded while preserving its commits and complete CI evidence.

## Fresh-base replacement and final merge

A fresh branch was created from the then-current protected `main` and the same bounded final implementation was reapplied as PR #159 (`APL-IP-003 Slice 21 final — regression naming & repository hygiene`). The resulting diff was exactly eight files:

- canonical-source workflow wiring;
- six maintained test files containing the 15 semantic renames;
- the new repository-hygiene guard.

Final head:

- `a59fd4c955c5c9534d74f7f58187d9012b514710`

PR #159 again completed all 9 triggered workflows successfully. On this fresh base the protected required `build` context was accepted normally. Windows installer validation again passed pinned Inno Setup, product-version and sovereignty checks, portable-baseline verification, predecessor lifecycle fixture, canonical installer compile, fresh/upgrade/repair/uninstall E2E, and Gate R6.

Implementation merge into protected `main`:

- PR #159;
- merge commit `0b01c035eaf5e12ec4c940071762936b850b01ff`.

## Final result

- historical `sliceN` regression-name debt: **15 -> 0**;
- stale current repository references outside explicit historical evidence: **0**;
- permanent cross-platform guards: **enabled**;
- sealed application version: **0.2.3 unchanged**;
- production runtime behavior: **unchanged**;
- recovery/network safety contract: **unchanged**;
- Git history/provenance: **preserved**;
- AI/bot identity history: **not reassigned or falsified**.

## Governance boundary

This engineering slice does not constitute legal approval of a post-refactor clean-IP baseline. The named author-to-ООО rights-basis execution and final human/legal review remain separate gates. No clean-IP APPROVED status or tag is authorized by this slice.

## Next bounded slice

**APL-IP-003 Slice 22 — application/backend boundary & production-source history cleanup.**

Extend maintained-source hygiene across the remaining application/platform boundary modules, remove obsolete APL task/milestone narration from root production Python, retire misleading historical private compatibility terminology where repository-wide evidence proves it internal-only, and guard GUI/application layering so GUI entry points consume common application seams rather than importing concrete platform backends directly. Preserve real legacy/recovery-format semantics and the sealed `0.2.3` behavior contract.
