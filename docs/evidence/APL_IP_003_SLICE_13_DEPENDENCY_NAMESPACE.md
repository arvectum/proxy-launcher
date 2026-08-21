# APL-IP-003 Slice 13 — core dependency namespace decoupling

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Purpose

Reduce use of the mutable `proxy_core` compatibility module as a generic standard-library service locator while preserving behavior-sensitive compatibility seams and the sealed Windows `0.2.3` runtime/release contract.

This is the first bounded dependency-decoupling tranche. State-heavy filesystem/configuration/portable bootstrap dependencies remain for a later slice.

## Baseline and merge

- pre-slice protected `main`: `9f6ca384be5347aa6a0ec16c5471b2c385f192d3`
- implementation PR: `#142`
- final reviewed implementation head: `cce1143ec132cd71106df2fcace357297f970e96`
- implementation merge: `728e3a69de9fcbb01c6b85bd652a624caad214ab`
- product version: `0.2.3` unchanged

## Bounded source changes

### `routing_policy.py`

Ordinary dependencies are now module-local:

- `io`
- `os`
- `re`

The mutable core seam remains only for behavior/configuration collaborators such as `no_proxy_path`, `_log`, `clean_domain`, `_atomic_write_text`, `_normalize_host`, `DEFAULT_NO_PROXY`, `load_no_proxy`, and `load_settings`.

### `local_proxy_transport.py`

Ordinary dependencies are now module-local:

- `base64`
- `re`
- `select`
- `socket`
- `struct`
- `threading`

The core seam remains for routing/logging/application collaborators (`load_settings`, `_normalize_host`, `host_bypasses_proxy`, `build_pac`, `_SOCKS5_REPLY_BIND_ADDR`, `_log`). The implementation no longer performs `core.socket`, `core.select`, `core.struct`, `core.re`, `core.base64`, or `core.threading` lookups.

### `process_supervision.py`

Ordinary dependencies are now module-local:

- `io`
- `json`
- `os`
- `socket`
- `subprocess`
- `sys`

The mutable core seam remains for behavior-sensitive ownership/status/path/logging collaborators. The implementation no longer performs `core.io`, `core.json`, `core.os`, `core.socket`, `core.subprocess`, or `core.sys` lookups.

## Compatibility-shell result

`proxy_core_legacy.py` no longer imports/exposes these non-contractual service-locator modules:

- `re`
- `select`
- `struct`

`socket` remains intentionally exported as an established monkeypatch compatibility alias. This is not an implementation dependency: `local_proxy_transport` and `process_supervision` use their own module-local `socket` import, and Python resolves all of those names to the same stdlib module object. Therefore historical tests and external monkeypatches against `core.socket.socket`, `core.socket.create_connection`, and related socket members still affect the live transport/probe behavior without requiring maintained runtime code to look up socket through core.

The `sys.modules` identity boundary remains unchanged in this slice.

## Guard changes

`tests/test_legacy_compatibility_shell.py` now proves that:

1. `re`, `select`, and `struct` are absent from the composed core namespace;
2. exact AST attributes `core.re`, `core.select`, and `core.struct` do not occur in any canonical runtime owner;
3. the three decoupled owners do not use the broader prohibited stdlib service-locator lookups defined for this tranche;
4. `core.socket is local_proxy_transport.socket is process_supervision.socket`;
5. neither decoupled implementation references `core.socket`;
6. no runtime `def`, `class`, async function, or lambda exists in `proxy_core_legacy.py`;
7. no live project callable is owned by `proxy_core_legacy`;
8. every live project callable exposed through the composed core has an explicit canonical owner.

## Self-review findings and corrections

Two useful failures occurred before the final reviewed head and were corrected rather than hidden.

### 1. Static-guard false positive

The first global guard used substring matching for names such as `core.struct`. It falsely matched `core.structured_logger` in `logging_bridge.py`. The macOS canonical-source job caught this. The guard was replaced by AST parsing that checks exact `core.<attribute>` access. This was a guard defect, not a runtime regression.

### 2. `core.socket` is a real compatibility seam

The first shell reduction removed the `socket` export together with the other candidate stdlib names. Canonical-source tests passed, but the full Windows clean-build suite exposed nine failures in network/transport tests because those tests deliberately monkeypatch `core.socket` to model loopback binding, DNS/network changes, direct routing and PAC health behavior.

The correct boundary was therefore refined:

- restore only the `core.socket` module alias;
- keep transport and supervision implementations on module-local `socket` imports;
- prove those local imports and `core.socket` are the same Python module object;
- retain static guards preventing implementation lookup through `core.socket`.

No other removed dependency was restored.

## Final implementation CI evidence

Final reviewed head `cce1143ec132cd71106df2fcace357297f970e96` completed all workflows triggered by this bounded change: **14/14 SUCCESS**.

- APL-IP-003 canonical source — Ubuntu/macOS/Windows matrix success
- Core backend contract — success
- APL-LNX-006 Linux diagnostics support bundle — success
- Windows P0 portable — success, including full clean-build unit suite and Documents execution smoke
- Windows installer — success, including portable baseline, synthetic predecessor fixture, canonical installer compile, fresh/upgrade/repair/uninstall E2E and Gate R6
- APL-IP-002-WIN controlled offline build — success, including official CPython Sigstore verification, exact Windows wheelhouse, offline canonical portable build and no package-index fallback proof
- macOS packaging — Apple Silicon and Intel success
- APL-LNX-007 Debian package — Ubuntu 22.04 and 24.04 success
- APL-LNX-008 AppImage — success
- SAST — success
- Secret scan — success
- Dependency vulnerability scan — success
- SBOM — success
- APL-IP-001 provenance — success

## Behavioral and governance result

- sealed Windows `0.2.3` behavior remains the reference contract;
- no product feature was added or removed;
- network ownership/recovery semantics were not weakened;
- historical Git/provenance evidence was not rewritten;
- the legacy module remains a compatibility/state/import shell and not a second runtime implementation;
- engineering completion does **not** constitute clean-IP approval;
- the author-to-ООО rights-basis and final post-refactor human/legal review remain required before any clean-IP candidate can be APPROVED or tagged.

## Next bounded slice

**APL-IP-003 Slice 14 — state/bootstrap dependency namespace decoupling.**

Inventory and decouple the remaining non-contractual stdlib/service-locator dependencies in the state-heavy bootstrap owners, especially `application_filesystem.py`, `configuration_storage.py`, and `portable_lifecycle.py`, while explicitly preserving any dependency aliases proven to be behavior-sensitive monkeypatch seams. The `sys.modules` module-identity boundary remains outside that slice unless independently proven safe.
