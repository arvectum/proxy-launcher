# APL-LNX-003 — Linux/Astra runtime preflight enforcement & capability UX

Status: implemented

## Goal

Wire APL-LNX-002 into the real runtime boundary so Linux/Astra never starts a new system-proxy mutation unless the current NetworkManager host is operationally ready, while keeping disable/recovery paths available if readiness later degrades.

## Runtime separation

APL-LNX-003 separates two different questions:

1. **Product support** — Linux/Astra has a governed backend and supports system proxy, bypass rules and safe rollback.
2. **Current-host readiness** — this specific machine currently has usable NetworkManager state and sufficient authorization to apply the backend safely.

A supported platform is therefore not automatically treated as an operational host.

## Operational states

`backend_runtime.operational_status_for_platform()` returns immutable `BackendOperationalStatus` evidence.

For Linux/Astra it maps APL-LNX-002 to:

- `ready` — enable/reconfiguration may proceed;
- `auth_required` — NetworkManager is technically capable but PolicyKit authorization is required; mutation is blocked until an explicit authorization flow exists;
- `unavailable` — the host cannot safely accept a new NetworkManager proxy mutation.

Windows and macOS retain their existing runtime path and are reported ready by this gate; their own platform hardening remains governed by their dedicated tasks.

## Mutation boundary

The runtime facade now gates:

- `enable_system_proxy()`;
- `sync_client_no_proxy()`.

The following paths are deliberately **not** gated:

- `disable_system_proxy()`;
- `system_proxy_enabled()`;
- `network_restore_pending()`.

This is a safety requirement. A machine that was ready at enable time can later lose NetworkManager connectivity, permissions, or session state. Arvectum must not use that degradation as a reason to make rollback unreachable.

## User-facing capability UX

`backend_runtime.operational_status_view()` and `proxy_core.backend_operational_view()` expose stable product data:

- platform label;
- operational state;
- badge (`Доступно`, `Нужно разрешение`, `Недоступно`);
- whether enable is currently allowed;
- localized title and explanatory message;
- read-only preflight reasons.

The UX does not expose raw command failures as the primary message and does not tell the user that Linux support is absent merely because one host is not ready.

### PolicyKit case

`auth_required` is intentionally not equivalent to `ready`. Until the product implements an explicit authorization flow, Arvectum reports that NetworkManager needs permission and leaves the network unchanged.

### Unavailable case

The user-facing message states that NetworkManager is not currently ready and that the network has been left unchanged. This avoids an ambiguous generic “proxy failed” result.

## Safety properties

- preflight remains read-only;
- no automatic package installation;
- no `sudo`;
- no implicit PolicyKit prompt;
- no NetworkManager restart;
- no interface cycling;
- no new mutation reaches `LinuxBackend.enable()` or `sync_no_proxy()` unless readiness is `ready`;
- rollback/disable remains callable even after preflight degradation.

## Verification

`tests/test_linux_runtime_preflight_wiring.py` covers:

1. ready Linux/Astra mapping and UX;
2. `auth_required` mapping without false readiness;
3. unavailable mapping and safe user message;
4. governed exception from the enable gate;
5. unchanged Windows/macOS operational behavior;
6. enable blocked before backend mutation;
7. no-proxy synchronization blocked before backend mutation;
8. disable still available when preflight would fail;
9. rollback inspection still available when preflight would fail.

The existing APL-LNX-002 suite continues to own detailed NetworkManager probing behavior.
