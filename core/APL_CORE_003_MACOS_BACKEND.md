# APL-CORE-003 — macOSBackend

Status: implemented.

## Goal

Add a concrete macOS implementation of the platform-neutral `ProxyBackend`
contract introduced by APL-CORE-001, without changing the customer-confirmed
Windows 0.2.3 runtime or the APL-CORE-002 Windows adapter.

The backend establishes a safe OS-mutation boundary for macOS. Automatic
backend selection from ProxyCore/GUI remains a later integration task.

## Implementation

`macos_backend.py` defines `MacOSBackend(ProxyBackend)` with:

- `backend_id == "macos"`;
- `enable(config)`;
- `disable()`;
- `is_enabled(config)`;
- `restore_pending()`;
- `sync_no_proxy(config)`.

The backend uses `/usr/sbin/networksetup` through a typed, injectable
`NetworkSetupClient`. No shell is used.

For every enabled macOS network service present when `enable()` is called, the
backend snapshots:

- Automatic Proxy Configuration enabled state;
- Automatic Proxy Configuration URL;
- existing proxy bypass domains.

The durable rollback document is stored by default at:

`~/Library/Application Support/Arvectum/ProxyLauncher/macos_proxy_backup.json`

The file is written atomically before the first `networksetup -set...` command.
The product's no-proxy entries are merged with pre-existing bypass domains
rather than replacing them.

## Safety model

1. **Backup before mutation.** If the complete snapshot cannot be read and
   persisted, `enable()` returns `False` and performs no system mutation.
2. **Partial-enable rollback.** If a later service mutation fails, every touched
   service is restored in reverse order. Rollback evidence is cleared only when
   that rollback completes.
3. **Ownership-aware disable.** Before restoring anything, `disable()` verifies
   that each still-present snapshotted service still has the exact Arvectum PAC
   URL and expected bypass state. A foreign/user/admin change makes disable fail
   closed; the newer state is not overwritten and rollback evidence remains.
4. **No generic reset.** Calling `disable()` without rollback evidence is an
   idempotent no-op.
5. **Corrupt evidence stays visible.** `restore_pending()` is based on durable
   evidence existence. An unreadable backup therefore remains pending rather
   than being silently replaced.
6. **Bypass preservation.** `sync_no_proxy()` updates only the Arvectum-added
   bypass component while preserving entries that existed before ownership.
7. **Configuration identity.** PAC URL and local HTTP proxy URL are retained as
   the configuration identity. `sync_no_proxy()` cannot silently switch either.

## Network-service behavior

The first enable snapshots all currently enabled network services and applies
the PAC/bypass configuration to each of them. Services that are disabled at
that moment are intentionally not touched.

If a snapshotted service disappears before disable, it is not recreated or
mutated by name. Existing snapshotted services are restored only after the
ownership check succeeds for all of them.

## Contract tests

`tests/test_macos_backend.py` covers:

- concrete backend shape and stable ID;
- snapshot-before-mutation behavior;
- preservation of existing bypass entries;
- exact rollback and idempotent disable;
- protection from foreign PAC changes;
- partial-enable rollback;
- safe no-proxy synchronization;
- fail-closed configuration mismatch;
- corrupt rollback evidence;
- parsing/error behavior of the `networksetup` adapter.

A dedicated core-backend workflow runs the platform-neutral, Windows-adapter,
and macOS-adapter contract tests on Linux and macOS runners. The macOS leg also
checks, non-destructively, that the required `networksetup` command family is
present on the runner.

## Acceptance

- `MacOSBackend` is a concrete `ProxyBackend` implementation.
- It is importable and unit-testable on non-macOS CI runners.
- Rollback evidence is durable before system mutation.
- Existing user bypass entries survive enable/sync/disable.
- Foreign proxy/PAC state is never overwritten during disable.
- Partial enable failures attempt precise restoration and preserve pending
  evidence when restoration cannot be proven complete.
- Existing Windows runtime code and `WindowsBackend` are unchanged.
- Automatic backend selection is not introduced by this task.

## Explicitly deferred

APL-CORE-003 does not yet:

- select `MacOSBackend` automatically from ProxyCore, GUI, or CLI;
- watch for network services created/activated after `enable()`;
- add a privileged helper or product UX around any macOS authorization prompt;
- perform destructive acceptance against a physical Mac's real network
  configuration;
- package/notarize/sign the final macOS application.

Those concerns remain separate integration/productization tasks so the backend
safety contract can be reviewed and tested independently first.
