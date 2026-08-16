# APL-CORE-002 — WindowsBackend

Status: implemented.

## Goal

Introduce the concrete Windows implementation of the `ProxyBackend` contract
without changing the customer-confirmed Windows 0.2.3 proxy mutation and
rollback path.

APL-CORE-001 established the platform-neutral interface. APL-CORE-002 adds the
Windows adapter that can be selected by later backend-resolution/application
wiring while keeping the proven registry, environment-variable, recovery and
rollback implementation in `proxy_core.py` unchanged.

## Implementation

`windows_backend.py` defines `WindowsBackend(ProxyBackend)` with the complete
contract:

- `backend_id == "windows"`;
- `enable(config)`;
- `disable()`;
- `is_enabled(config)`;
- `restore_pending()`;
- `sync_no_proxy(config)`.

The adapter delegates to the existing Windows entry points:

| WindowsBackend | Proven Windows implementation |
| --- | --- |
| `enable(config)` | `proxy_core.enable_system_proxy()` |
| `disable()` | `proxy_core.disable_system_proxy()` |
| `is_enabled(config)` | `proxy_core.system_proxy_enabled()` |
| `restore_pending()` | `proxy_core.network_restore_pending()` |
| `sync_no_proxy(config)` | `proxy_core.sync_client_no_proxy()` |

This preserves the already-tested WinINET backup/restore, user environment
backup/restore, recovery-autostart ownership rules and foreign-proxy safety.

## Configuration-specific safety bridge

The legacy Windows entry points still resolve their values from the existing
application state. To satisfy the new backend contract without pretending that
arbitrary caller values were applied, `WindowsBackend` resolves the exact values
that the legacy path would use and compares them with the supplied
`ProxyBackendConfig` before `enable`, `is_enabled`, or `sync_no_proxy` delegates.

The comparison covers:

- exact PAC URL;
- exact local HTTP proxy URL;
- normalized, de-duplicated no-proxy entries, including the built-in Windows
  safety exclusions and current application exclusions.

A mismatch is fail-closed: no Windows mutation function is called and the
operation returns `False`.

This guard is intentionally transitional. A later core integration task can
move resolved configuration ownership fully above the backend without changing
the `ProxyBackend` contract.

## Dependency boundary

`windows_backend.py` imports only the platform-neutral `proxy_backend` module at
module import time. `proxy_core` is loaded lazily when a default backend
instance is constructed and can be dependency-injected in tests. Therefore the
Windows backend module remains importable on non-Windows CI runners and does not
import `winreg` directly.

## Safety invariants preserved

1. Durable WinINET/environment rollback evidence is still created before the
   existing mutation path changes Windows settings.
2. `disable()` continues to rely on the existing ownership-aware restoration
   code and does not introduce a generic network reset.
3. A foreign PAC/proxy cannot be treated as this backend merely because some
   proxy is active.
4. `is_enabled(config)` is configuration-specific: a mismatched configuration
   returns `False` without querying success from the legacy active-state check.
5. `restore_pending()` exposes the existing durable backup evidence unchanged.
6. `sync_no_proxy(config)` delegates only when the supplied exclusion set is the
   set the existing Windows runtime will actually apply.

## Acceptance

- `WindowsBackend` is a concrete `ProxyBackend` implementation.
- `backend_id` is stable and equals `windows`.
- The adapter is importable without direct Windows-only dependencies.
- Matching resolved configuration delegates to the proven Windows functions.
- PAC, HTTP-proxy or no-proxy mismatch fails closed and performs no mutation.
- No-proxy matching is case-normalized and de-duplicated.
- Existing Windows 0.2.3 runtime code is not modified by this task.
- Unit tests cover the complete adapter lifecycle and fail-closed semantics.

## Explicitly deferred

APL-CORE-002 does not yet select this backend automatically from `proxy_core`,
the GUI, or CLI. Backend selection/application wiring is intentionally kept
separate so adding macOS and Linux implementations does not destabilize the
customer-confirmed Windows baseline.
