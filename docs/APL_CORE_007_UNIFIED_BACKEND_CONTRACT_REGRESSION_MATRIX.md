# APL-CORE-007 — Unified backend contract & regression matrix

## Goal

Freeze one platform-neutral system-proxy backend contract for Windows, macOS and Linux/Astra Linux, and make release-critical regressions explicit and executable.

APL-CORE-007 does **not** replace the concrete backends introduced by APL-CORE-002/003/004 and does not reimplement the customer-proven Windows mutation path. It governs the surface already wired by APL-CORE-005 and the capability model introduced by APL-CORE-006.

## Canonical backend surface

Every governed backend must remain a complete `ProxyBackend` implementation with exactly these five public operations:

| Operation | Input | Contract |
|---|---|---|
| `enable` | resolved `ProxyBackendConfig` | Save rollback evidence before applying Arvectum-owned proxy state. |
| `disable` | — | Restore only Arvectum-owned/proven state; do not destroy foreign settings. |
| `is_enabled` | resolved `ProxyBackendConfig` | Return true only for the supplied Arvectum configuration. |
| `restore_pending` | — | Report incomplete durable rollback evidence fail-closed. |
| `sync_no_proxy` | resolved `ProxyBackendConfig` | Update bypass entries while preserving pre-existing user entries. |

`backend_contract.py` validates this surface without instantiating a backend or mutating the host OS. Signature drift or a missing abstract member fails CI.

## Governed backend registry

The executable registry must stay one-to-one with `capability_model.declared_backend_ids()`:

- `windows` → `WindowsBackend`
- `macos` → `MacOSBackend`
- `linux` → `LinuxBackend` (including Astra Linux through the Linux/NetworkManager path)

Adding a backend without a capability declaration, or declaring a backend without a concrete class, is a contract failure.

## Regression matrix

| Requirement | Windows | macOS | Linux/Astra | Mandatory invariant |
|---|:---:|:---:|:---:|---|
| `CONTRACT-001` | ✓ | ✓ | ✓ | Complete canonical five-operation backend surface. |
| `LIFECYCLE-001` | ✓ | ✓ | ✓ | Configuration-specific enable/status/sync/disable lifecycle. |
| `ROLLBACK-001` | ✓ | ✓ | ✓ | Durable ownership-aware rollback, fail-closed on uncertainty. |
| `FOREIGN-001` | ✓ | ✓ | ✓ | Foreign/admin proxy settings are preserved. |
| `BYPASS-001` | ✓ | ✓ | ✓ | Existing user bypass entries are preserved. |
| `RUNTIME-001` | ✓ | ✓ | ✓ | Exactly one governed backend selected per supported platform. |
| `CAPABILITY-001` | ✓ | ✓ | ✓ | Backend registry and capability registry remain synchronized. |
| `WINDOWS-BASELINE-001` | ✓ | — | — | Proven Windows 0.2.3 mutation path stays behind the adapter. |

The authoritative machine-readable rows live in `backend_contract.REGRESSION_MATRIX`; this table is explanatory documentation only.

## Required cross-platform capabilities

For every governed backend, these capabilities must stay `supported`:

- `system_proxy`
- `bypass_rules`
- `safe_rollback`

Platform-specific or future product features such as autostart and application routing remain governed by APL-CORE-006 and are not promoted merely because the backend contract is satisfied.

## CI gate

`.github/workflows/core-backends.yml` compiles and executes the unified contract matrix together with the existing backend-specific regression suites on Linux and macOS runners. The backend-specific suites remain the behavioral evidence; `tests/test_backend_contract_matrix.py` is the meta-regression guard that prevents the three implementations from silently drifting into different APIs or coverage obligations.

## Definition of done

APL-CORE-007 is complete when:

1. `backend_contract.py` is the canonical executable contract manifest.
2. Windows, macOS and Linux classes all validate against it.
3. Every governed backend has the mandatory regression requirements.
4. Backend and capability registries are one-to-one.
5. Required safety capabilities are supported on all governed backends.
6. Signature drift fails tests.
7. Core backend CI includes the contract matrix test.
8. Existing Windows/macOS/Linux behavioral suites remain green.
