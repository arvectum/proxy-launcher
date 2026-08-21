# APL-IP-003 Slice 12 — legacy compatibility shell reduction evidence

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Canonical merge

- Pull request: `#140` — `APL-IP-003 Slice 12 — legacy compatibility shell reduction`
- Merge commit: `12e562538ddb1f98eca2f610867b6b5f928d6985`
- Pre-slice main baseline: `bce87b3641404178a1ab87b4fd94451074def697`
- Reviewed final PR head: `51182eac6e4ae3b7b2f67a74d649b7e4732888de`
- Product version: unchanged (`0.2.3`)
- Final implementation diff changed exactly four files: `.github/workflows/apl-ip-003-canonical-source.yml`, `proxy_core.py`, `proxy_core_legacy.py`, and `tests/test_legacy_compatibility_shell.py`.
- Diff size: 141 additions / 2491 deletions. `proxy_core_legacy.py` alone removed 2485 lines of duplicated implementation.

## Resulting ownership boundary

Before Slice 12, the maintained `proxy_core_legacy.py` still contained historical copies of runtime functions/classes even though Slices 1–11 already installed canonical implementations over them at composition time.

After Slice 12, `proxy_core_legacy.py` is only the mutable compatibility/state shell used by `proxy_core.py` during canonical composition. It contains no maintained runtime implementation.

The shell retains only:

- shared standard-library module dependencies still consumed through the mutable core namespace: `base64`, `hashlib`, `io`, `json`, `os`, `re`, `select`, `socket`, `struct`, `subprocess`, `sys`, `threading`, and `time`;
- release identity: `APP_VERSION = "0.2.3"`, `ENGINEERING_MILESTONE = "P0.2"`;
- state/bootstrap values: `_STATE_FILES` and mutable `_STATE_READY`;
- portable/install identity and compatibility state: `_INSTALL_OWNER_MARKER`, `_INSTALL_OWNER_VALUE`, `_LEGACY_INSTALL_OWNER_VALUES`, `_LAUNCHER_EXE_NAME`, `_USER_AUTOSTART_RUN_VALUE`, and `_LAST_SELF_HEAL_ERROR`.

All historical runtime implementation remains preserved in Git history and prior provenance evidence. Slice 12 removes duplicated maintained source; it does not rewrite or erase historical provenance.

## Live callable ownership guard

`tests/test_legacy_compatibility_shell.py` now provides a permanent executable inventory/guard:

1. `proxy_core` and `proxy_core_legacy` must resolve to the same established mutable module object after canonical composition.
2. `proxy_core_legacy.py` is parsed with `ast` and any `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, or `Lambda` is rejected.
3. No live runtime callable exposed through composed `proxy_core` may have `__module__ == "proxy_core_legacy"`.
4. Every live project function/class must belong to the explicit canonical-owner set.
5. Representative seams across every bounded extraction area are checked by exact owner module, including filesystem, portable lifecycle, logging, configuration, routing, transport, process supervision, Recovery Run, WinINET persistence, system-proxy composition, orphan PAC recovery, and application runtime.
6. The exact release/state/install identity required before or across composition remains present.

The APL-IP-003 canonical-source workflow compiles and executes this guard on Ubuntu, macOS, and Windows.

## Compatibility deliberately retained

Slice 12 does **not** remove the established module identity boundary:

```python
sys.modules[__name__] = _core
```

`import proxy_core` still returns the same mutable module object used by existing monkeypatch-based tests and runtime collaborators. Only duplicate implementation was removed.

Retiring this identity is a later independent decision and requires its own evidence. It is not inferred merely from successful duplicate-code removal.

## Behaviour and release safety

The sealed `0.2.3` behavior remains the reference contract. The shell reduction changes source ownership/duplication only; no user-facing feature, routing policy, recovery rule, registry mutation, configuration schema, CLI contract, or package version was intentionally changed.

Independent regression evidence confirms that the reduced shell supplies everything still required by composed and frozen execution:

- canonical-source inventory/owner guard passed on Ubuntu, macOS, and Windows;
- Phase 5 config/security full unit suites passed on Ubuntu and Windows;
- structured logging/redaction full unit suites passed on Ubuntu and Windows;
- Doctor and Windows diagnostics/privacy full suites passed, including native Windows smoke checks;
- Windows portable clean build and Documents execution smoke passed;
- Windows installer fresh/upgrade/repair/uninstall E2E and Gate R6 passed;
- macOS packaging passed;
- Debian packaging passed on Ubuntu 22.04 and 24.04, including frozen artifact and package inspection;
- AppImage frozen build, inspection, and artifact generation passed;
- controlled offline Windows build passed from Sigstore-verified CPython and exact wheelhouse, with explicit proof of no package-index fallback.

## Implementation workflow evidence — 18/18 SUCCESS

- `32499273616` — APL-LNX-006 Linux diagnostics support bundle
- `32499273649` — Secret scan
- `32499273693` — SAST
- `32499273700` — Core backend contract
- `32499273624` — APL-IP-003 canonical source
- `32499273882` — APL-IP-001 provenance
- `32499273683` — APL-DIAG-001/002 structured logging + secret redaction
- `32499273841` — SBOM
- `32499273729` — APL-DIAG-004 Doctor
- `32499273991` — Dependency vulnerability scan
- `32499273612` — Phase 5 Config and Security
- `32499273800` — APL-DIAG-003/006 Windows diagnostics + privacy
- `32499273600` — macOS packaging
- `32499273694` — APL-LNX-007 Debian package
- `32499273888` — APL-LNX-008 AppImage
- `32499273790` — Windows P0 portable
- `32499273667` — Windows installer
- `32499273679` — APL-IP-002-WIN controlled offline build

## Governance

This engineering completion does not declare a clean-IP candidate APPROVED and does not authorize a clean-IP tag. The APL-IP-001 author-to-ООО rights-basis execution and final human/legal post-refactor review remain mandatory gates.

## Next bounded slice

**APL-IP-003 Slice 13 — core dependency-namespace decoupling.**

Inventory canonical owners that still use the mutable core object as a service locator for ordinary standard-library dependencies (`core.os`, `core.json`, `core.socket`, etc.). Replace non-contractual dependency lookups with module-local imports or narrow explicit dependencies while retaining only genuinely behavior-sensitive mutable collaborator seams. Then reduce the compatibility shell imports/state further. Removal of the `sys.modules` module-identity boundary remains out of scope until independently proven safe.
