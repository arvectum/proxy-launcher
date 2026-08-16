# APL-CORE-004 — LinuxBackend (Linux/Astra)

Status: implemented.

## Goal

Add a concrete Linux implementation of the platform-neutral `ProxyBackend`
contract introduced by APL-CORE-001, with Astra Linux as a first-class target,
without changing the customer-confirmed Windows runtime or the APL-CORE-002 / 003
Windows and macOS adapters.

APL-CORE-004 establishes the Linux OS-mutation and rollback boundary only.
Automatic backend selection from ProxyCore/GUI remains a later integration task.

## Platform strategy

`linux_backend.py` implements Linux system-proxy ownership through NetworkManager
and its command-line API, `nmcli`.

This is intentionally not a GNOME-only `gsettings` implementation. The backend
therefore works at the NetworkManager connection-profile layer and is suitable
for NetworkManager-managed Astra Linux desktop installations as well as other
NetworkManager-based Linux distributions.

The current backend deliberately fails closed when:

- `nmcli` / NetworkManager is unavailable;
- NetworkManager has no supported active connection profile;
- the active network is managed only by `networking`, ifupdown, systemd-networkd,
  or another non-NetworkManager stack;
- the caller lacks permission to inspect or modify the relevant profiles.

A non-NetworkManager fallback is explicitly deferred rather than silently
editing `/etc/network/interfaces`, environment files, or desktop-specific state.

## Implementation

`LinuxBackend(ProxyBackend)` provides:

- `backend_id == "linux"`;
- `enable(config)`;
- `disable()`;
- `is_enabled(config)`;
- `restore_pending()`;
- `sync_no_proxy(config)`.

`NetworkManagerClient` invokes `/usr/bin/nmcli` directly as an argument vector;
no shell is used. `LC_ALL=C` is forced for parse-stable command output and
subprocess calls have a bounded timeout.

For each supported active NetworkManager profile present when `enable()` is
called, the backend snapshots:

- connection UUID;
- connection type;
- active device name;
- `proxy.method`;
- `proxy.browser-only`;
- `proxy.pac-url`;
- `proxy.pac-script`.

VPN and loopback active profiles are intentionally not taken over. Other active
NetworkManager profiles with a real device are eligible and are tracked by UUID,
not by mutable display name.

The Arvectum-owned state is:

- `proxy.method = auto`;
- `proxy.browser-only = no`;
- `proxy.pac-url = config.pac_url`;
- `proxy.pac-script` cleared so the URL is authoritative.

After each active profile modification the backend calls `nmcli device reapply`
for that device. It does not restart NetworkManager and does not cycle the
network interface.

## Durable rollback evidence

The default rollback document is stored under the XDG state directory:

`$XDG_STATE_HOME/Arvectum/ProxyLauncher/linux_proxy_backup.json`

When `XDG_STATE_HOME` is not set, the fallback is:

`~/.local/state/Arvectum/ProxyLauncher/linux_proxy_backup.json`

The file is created atomically with restrictive permissions before the first
persistent `nmcli connection modify` call.

## Safety model

1. **Backup before mutation.** The complete set of target profiles and their
   original proxy properties must be readable and durably persisted before the
   first profile change.
2. **Reapply is part of mutation success.** A profile edit is not considered
   successfully applied until `nmcli device reapply` succeeds for its active
   device.
3. **Partial-enable rollback.** If profile modification or reapply fails, every
   touched profile is restored in reverse order. Rollback evidence is cleared
   only if that restoration succeeds completely.
4. **UUID ownership.** Profiles are tracked by NetworkManager UUID so display
   name changes do not redirect rollback to a different profile.
5. **Profile-type guard.** If an existing owned UUID now has a different
   connection type, disable refuses to mutate it.
6. **Foreign proxy protection.** Before restoring anything, disable verifies
   that every still-existing owned profile still has the exact Arvectum proxy
   state. A user/admin change makes disable fail closed and leaves evidence.
7. **Deleted profiles are not recreated.** A snapshotted UUID that no longer
   exists is skipped rather than re-created.
8. **Inactive owned profiles are still restored.** Persistent proxy settings are
   restored even when a formerly active profile is now inactive; only currently
   active profiles receive `device reapply`.
9. **No generic reset.** Disable without rollback evidence is an idempotent
   no-op.
10. **Corrupt evidence stays visible.** File existence alone makes
    `restore_pending()` true. Unreadable evidence is never replaced silently.
11. **New active profile is not assumed owned.** If a new supported active
    NetworkManager profile appears after enable, `is_enabled()` returns false
    rather than claiming coverage it cannot prove.

## `no_proxy` semantics on Linux

NetworkManager's WWW proxy setting exposes PAC URL/script state but does not
provide a separate per-profile bypass list. Arvectum's bypass policy therefore
remains encoded in the PAC document generated by ProxyCore.

For LinuxBackend:

- PAC generation remains outside the backend, as required by APL-CORE-001;
- `http_proxy_url` and `no_proxy` remain part of the owned configuration identity;
- `sync_no_proxy()` may update the durable expected `no_proxy` identity only
  after proving that the same PAC/local-proxy identity and owned NetworkManager
  state are still active;
- `sync_no_proxy()` never overwrites unrelated NetworkManager properties.

This keeps ownership boundaries explicit: ProxyCore owns PAC contents;
LinuxBackend owns the NetworkManager pointer to that PAC.

## Tests

`tests/test_linux_backend.py` covers:

- concrete backend shape and stable ID;
- backup-before-mutation ordering;
- exclusion of VPN profiles;
- exact persistent-profile rollback;
- inactive-profile restoration without unnecessary reapply;
- idempotent disable;
- foreign PAC protection;
- profile-type ownership protection;
- partial-enable rollback;
- preservation of pending evidence after rollback failure;
- no-proxy identity synchronization without NetworkManager mutation;
- PAC / HTTP identity mismatch rejection;
- corrupt rollback evidence;
- new unowned active-profile detection;
- fail-closed behavior with no supported active NetworkManager profile;
- nmcli parsing, escaping, and command-error behavior.

The shared core-backend GitHub Actions workflow compiles and runs the abstract,
Windows, macOS, and Linux backend contract tests on both Linux and macOS runners.
The Linux leg also verifies native `nmcli` availability; exact command vectors,
`device reapply` behavior, parsing, ownership, and rollback are covered by the
daemon-independent contract tests.

## Acceptance

- `LinuxBackend` is a concrete `ProxyBackend` implementation.
- Astra Linux is supported when the relevant desktop connections are managed by
  NetworkManager and the operator has sufficient NetworkManager permissions.
- The module is importable and unit-testable on non-Linux runners.
- Durable rollback evidence exists before persistent system mutation.
- Active profile changes are reapplied without deliberate interface down/up.
- Foreign user/admin proxy state is never overwritten during disable.
- Deleted profiles are not recreated and renamed profiles remain bound by UUID.
- Partial failures preserve recovery evidence unless complete rollback is proven.
- Existing Windows and macOS backend code remains unchanged.
- Automatic backend selection is not introduced by this task.

## Explicitly deferred

APL-CORE-004 does not yet:

- select `LinuxBackend` automatically from ProxyCore, GUI, or CLI;
- implement a fallback for Astra/Linux systems intentionally managed by
  `/etc/network/interfaces`, systemd-networkd, or another network manager;
- watch and take ownership of profiles activated after `enable()`;
- install/configure NetworkManager or modify PolicyKit/netdev membership;
- perform destructive acceptance against a physical Astra Linux workstation;
- package/sign the final Linux/Astra application.

Those concerns remain separate integration, compatibility, and productization
steps so the backend safety contract can be reviewed independently first.
