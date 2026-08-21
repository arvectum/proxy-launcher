# APL-IP-003 Slice 14 — state/bootstrap dependency namespace decoupling

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Purpose

Reduce use of the mutable `proxy_core` compatibility module as a generic standard-library service locator in the state/bootstrap ownership layer while preserving behavior-sensitive mutable collaborators and the sealed Windows `0.2.3` contract.

This slice follows Slice 13's routing/transport/supervision dependency decoupling and deliberately applies the same boundary to the state-heavy owners without prematurely deleting compatibility aliases that are still directly used by historical regression tests or other maintained owners.

## Baseline and merge

- pre-slice protected `main`: `c345473ffdbbca2a5cb57bc8d2c2b339c305b54e`
- implementation PR: `#144`
- final reviewed implementation head: `7fec26a78645ad69a8b2995cb7a2b36f912ff707`
- implementation merge: `63afab3e9428af7164d3c6dbcad810315e9784f7`
- product version: `0.2.3` unchanged

## Bounded source changes

### `application_filesystem.py`

Ordinary dependencies are now module-local:

- `io`
- `json`
- `os`
- `shutil`
- `sys`
- `tempfile`

The mutable core seam remains for canonical application/state collaborators and state such as `install_dir`, `data_dir`, `_temporary_roots`, `_legacy_state_dirs`, `_valid_state_file`, `_copy_state_atomically`, `migration_error_path`, `_STATE_FILES`, and `_STATE_READY`.

The implementation no longer performs `core.io`, `core.json`, `core.os`, or `core.sys` lookups.

### `configuration_storage.py`

Ordinary dependencies are now module-local:

- `base64`
- `hashlib`
- `io`
- `json`
- `os`
- `threading`
- `time`

The core seam remains for behavior-sensitive validators, configuration constants, path providers, atomic-write/recovery collaborators, DPAPI helper seams, `is_windows`, and `_log`. This intentionally preserves the existing ability to patch internal configuration behavior without making the core module the owner of ordinary stdlib dependencies.

The implementation no longer performs `core.base64`, `core.hashlib`, `core.io`, `core.json`, `core.os`, `core.threading`, or `core.time` lookups.

### `portable_lifecycle.py`

Ordinary dependencies are now module-local:

- `hashlib`
- `io`
- `os`
- `shutil`
- `subprocess`
- `sys`

The core seam remains for stable-path, ownership, logging, hash-check and mutable self-heal state collaborators such as `is_windows`, `stable_app_exe`, `_same_path`, `_sha256_file`, `_INSTALL_OWNER_MARKER`, `_INSTALL_OWNER_VALUE`, `_LAST_SELF_HEAL_ERROR`, `_log`, and `ensure_stable_app_copy`.

The implementation no longer performs `core.hashlib`, `core.io`, `core.os`, `core.subprocess`, or `core.sys` lookups.

## Compatibility alias result

`proxy_core_legacy.py` was intentionally **not changed** by the implementation PR.

Existing stdlib aliases remain available through the shared core namespace because established regression tests directly patch aliases including `core.os`, `core.io`, `core.sys`, and `core.subprocess`. The Slice 14 guard proves that the corresponding local imports in the canonical owners are the same Python module objects. Therefore those monkeypatches continue to affect live behavior without requiring maintained implementation code to resolve dependencies through core.

This is the same compatibility principle proven for `core.socket` in Slice 13.

Physical removal of retained aliases is deferred until repository-wide consumer inventory proves that an alias is no longer needed by any maintained owner or supported compatibility test.

The `sys.modules` module-identity boundary remains unchanged.

## Guard changes

`tests/test_legacy_compatibility_shell.py` now proves that:

1. state/bootstrap owners do not use their governed `core.<stdlib>` service-locator attributes;
2. `application_filesystem` local `os/io/sys` imports share module identity with retained compatibility aliases;
3. `configuration_storage` local `base64/hashlib/io/json/os/threading/time` imports share module identity with retained compatibility aliases;
4. `portable_lifecycle` local `hashlib/io/os/subprocess/sys` imports share module identity with retained compatibility aliases;
5. Slice 13's `socket` compatibility rule remains intact;
6. removed `re/select/struct` dependencies remain absent from core and all canonical owners;
7. no runtime `def`, `class`, async function, or lambda exists in `proxy_core_legacy.py`;
8. no live project callable is owned by `proxy_core_legacy`;
9. every live project callable exposed through the composed core has an explicit canonical owner.

The guard uses AST-exact `core.<attribute>` inspection rather than substring matching.

## Behavioral review

No runtime or compatibility correction was required after the final implementation head was opened. The existing shared-module alias model preserved tests that patch `core.os`, `core.io`, `core.sys`, and related module members.

High-value contract evidence included:

- Phase 5 Config and Security on Ubuntu and Windows: governed-module compile, targeted configuration-security tests, and full unit suite all SUCCESS;
- Windows P0 portable: canonical clean build and Documents execution smoke SUCCESS;
- Windows installer: portable baseline, synthetic predecessor fixture, canonical installer compile, fresh/upgrade/repair/uninstall E2E and Gate R6 SUCCESS;
- macOS packaging: Apple Silicon and Intel `.app`/DMG build and inspection SUCCESS;
- Debian packaging: SUCCESS;
- AppImage packaging: SUCCESS;
- canonical-source Ubuntu/macOS/Windows matrix: SUCCESS.

## Final implementation CI evidence

Final reviewed head `7fec26a78645ad69a8b2995cb7a2b36f912ff707` completed **12/12 workflows triggered by this bounded change: SUCCESS**.

- `32508319322` — Phase 5 Config and Security
- `32508319502` — Secret scan
- `32508319149` — SBOM
- `32508319236` — SAST
- `32508319130` — Dependency vulnerability scan
- `32508319181` — APL-IP-003 canonical source
- `32508319153` — APL-IP-001 provenance
- `32508319249` — APL-LNX-007 Debian package
- `32508319109` — macOS packaging
- `32508319085` — APL-LNX-008 AppImage
- `32508319160` — Windows P0 portable
- `32508319183` — Windows installer

Controlled-offline and unrelated diagnostics workflows were not triggered by this path set; this evidence does not claim that they ran for Slice 14.

## Behavioral and governance result

- sealed Windows `0.2.3` behavior remains the reference contract;
- no product feature was added or removed;
- state migration, configuration validation, DPAPI protection, atomic persistence, recovery/quarantine, portable self-heal and handoff semantics remain covered by green tests/builds;
- historical Git/provenance evidence was not rewritten;
- compatibility aliases remain only where not yet proven removable;
- engineering completion does **not** constitute clean-IP approval;
- the author-to-ООО rights-basis and final post-refactor human/legal review remain required before any clean-IP candidate can be APPROVED or tagged.

## Next bounded slice

**APL-IP-003 Slice 15 — platform/recovery dependency namespace decoupling & compatibility-alias inventory.**

Inventory the remaining canonical owners that still resolve ordinary stdlib dependencies through mutable core — especially platform/recovery/application-runtime modules — and localize safe dependencies while preserving behavior-sensitive collaborators. Build a repository-wide consumer map for retained `proxy_core_legacy` stdlib aliases and physically remove only aliases proven unused by maintained owners and supported compatibility tests. The `sys.modules` identity boundary remains outside that slice unless independently proven safe.
