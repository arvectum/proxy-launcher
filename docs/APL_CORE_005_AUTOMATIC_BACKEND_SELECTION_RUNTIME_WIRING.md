# APL-CORE-005 — Automatic backend selection & runtime wiring

**Status:** IMPLEMENTED  
**Scope:** Windows / macOS / Linux (including Astra Linux via NetworkManager)  
**Safety rule:** unsupported or unreadable platform state fails closed.

## Goal

Connect the platform-neutral `ProxyBackend` contract and the concrete backends from APL-CORE-002/003/004 to the real Proxy Launcher lifecycle without duplicating OS branches in the GUI or CLI.

## Runtime mapping

| `sys.platform` | Backend | Implementation |
|---|---|---|
| `win*` | `windows` | `WindowsBackend` |
| `darwin` | `macos` | `MacOSBackend` |
| `linux*` | `linux` | `LinuxBackend` / NetworkManager (`nmcli`) |
| anything else | unsupported | fail closed |

Astra Linux uses Python's Linux platform identifier and therefore selects `LinuxBackend` automatically.

## Wiring boundary

`proxy_core.py` is now a thin runtime facade. The pre-CORE-005 implementation is preserved byte-for-byte as `proxy_core_legacy.py`; Git history records the exact same blob under the new path.

The facade rewires only these public integration seams:

- `enable_system_proxy()`
- `disable_system_proxy()`
- `system_proxy_enabled()`
- `network_restore_pending()`
- `sync_client_no_proxy()`

Existing CLI functions (`--start`, `--stop`, `--rollback`, `--status`) resolve those names dynamically from the preserved module and therefore use the selected backend automatically. `proxy_gui.py` already calls the same public seams, so GUI status/start/stop behavior follows the same runtime selection without GUI platform branching.

## Resolved backend configuration

Every backend receives one immutable `ProxyBackendConfig` built at the runtime boundary:

```text
pac_url        = http://127.0.0.1:<local_pac_port><pac_path>
http_proxy_url = http://127.0.0.1:<local_http_port>
no_proxy       = normalized(DEFAULT_NO_PROXY + no_proxy.txt)
```

Normalization is stable, case-insensitive and de-duplicated. This also preserves the strict configuration-match guard in `WindowsBackend`.

## Windows compatibility

The established Windows 0.2.3 registry/environment/rollback implementation is not rewritten. Before runtime rewiring, the facade captures its five original public functions and exposes them through an internal adapter passed explicitly to `WindowsBackend`.

This prevents dispatch recursion and retains the customer-proven mutation path while making Windows participate in the same automatic backend composition model as macOS and Linux.

The facade also preserves the historical `proxy_core.py` `__file__` value for portable-install and recovery logic.

## Fail-closed behavior

If platform selection or a backend operation fails:

- enable: `False`
- disable/rollback: `False`
- enabled status: `False`
- no-proxy sync: `False`
- restore-pending inspection: `True`

The last rule is intentional: inability to prove rollback completeness must never produce a successful recovery UX.

## Tests

`tests/test_backend_runtime.py` verifies deterministic platform mapping and unsupported-platform rejection.

`tests/test_backend_runtime_wiring.py` verifies:

- one normalized config for all backend operations;
- one process-local selected backend;
- delegation of enable/disable/status/restore/no-proxy seams;
- fail-closed behavior when backend selection fails.

Existing Windows/macOS/Linux backend contract tests remain authoritative for each concrete implementation's ownership and rollback rules.
