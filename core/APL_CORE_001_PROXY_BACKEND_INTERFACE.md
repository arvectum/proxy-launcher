# APL-CORE-001 — ProxyBackend interface

Status: implemented.

## Goal

Create one explicit operating-system boundary between the platform-neutral proxy engine/application logic and code that reads or mutates system proxy settings.

This task intentionally does **not** extract the existing Windows implementation yet.  The customer-confirmed Windows 0.2.3 behaviour remains unchanged while the contract needed by later Windows/macOS/Linux backends becomes stable and testable.

## Public contract

`proxy_backend.py` defines:

- `ProxyBackendConfig` — immutable, resolved OS-facing values:
  - PAC URL;
  - local HTTP proxy URL;
  - normalized no-proxy/bypass entries.
- `ProxyBackend` — abstract lifecycle boundary:
  - `backend_id`;
  - `enable(config)`;
  - `disable()`;
  - `is_enabled(config)`;
  - `restore_pending()`;
  - `sync_no_proxy(config)`.

## Safety invariants

Every concrete backend must preserve the existing safety model:

1. Durable rollback evidence must exist before system settings are mutated.
2. Disable/rollback may restore only state owned or otherwise proven by Arvectum.
3. A foreign proxy/PAC must never be removed merely because some proxy is active.
4. `is_enabled()` is configuration-specific and ownership-aware.
5. Incomplete rollback evidence must remain observable through `restore_pending()` until recovery is complete.
6. Bypass synchronization must preserve bypass entries that existed before Arvectum took ownership.

## Boundary mapping from the current Windows implementation

The existing `proxy_core.py` functions map conceptually to the interface as follows:

| Current function | ProxyBackend contract |
| --- | --- |
| `enable_system_proxy()` | `enable(config)` |
| `disable_system_proxy()` | `disable()` |
| `system_proxy_enabled()` | `is_enabled(config)` |
| `network_restore_pending()` | `restore_pending()` |
| `sync_client_no_proxy()` | `sync_no_proxy(config)` |

The current Windows functions continue to run unchanged in APL-CORE-001.  Moving them behind a concrete Windows backend is a separate extraction step so this commit cannot disturb the proven Windows release baseline.

## Explicitly outside the backend boundary

The backend does not own:

- `ProxyCore` listener/transport lifecycle;
- upstream proxy connection/failover;
- PAC generation;
- `proxy_settings.json` and `no_proxy.txt` persistence;
- GUI policy;
- product versioning or release packaging.

Windows recovery-autostart mechanics may remain an implementation detail of the Windows backend because they exist specifically to guarantee safe restoration of Windows system proxy state.

## Acceptance

- The interface is importable without platform-specific dependencies.
- It cannot be instantiated directly.
- An incomplete concrete backend cannot be instantiated.
- Configuration objects are immutable.
- Contract tests prove configuration-specific enabled-state semantics and the complete lifecycle shape.
- No production Windows proxy mutation path is changed by this task.
