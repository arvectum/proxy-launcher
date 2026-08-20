# Windows signed-set lifecycle acceptance on an already-installed owner host

Task: `APL-REL-014`

Use `tools/windows_signed_set_lifecycle_acceptance_owner_host.ps1` when the owner Windows machine already has Arvectum Proxy Launcher registered by the installer.

The wrapper does not blindly uninstall an existing instance. It first requires the registered installation to be the exact governed 0.2.3 production build:

- application SHA-256 `f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a`;
- cached repair installer SHA-256 `5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414`;
- manifest version `0.2.3` and matching application hash;
- expected Arvectum AppId registration under HKCU;
- expected display name/version;
- no running Launcher process;
- no active network recovery backup files.

A machine-wide, ambiguous, old, modified or incomplete registered installation remains a fail-closed `BLOCK` before any mutation.

For an exact existing installation, the wrapper snapshots before mutation:

1. install root;
2. LocalAppData application state;
3. Arvectum Run values;
4. exact HKCU uninstall registration via `reg.exe export`;
5. installer-created Start Menu/Desktop shortcuts.

It then removes the snapshot from the active host, invokes the canonical `tools/windows_signed_set_lifecycle_acceptance.ps1`, and restores the original snapshot in `finally` even if lifecycle acceptance fails.

Successful evidence keeps the canonical APL-REL-014 fields and additionally records:

- `preexisting_registered_install = true`;
- `preexisting_registered_install_exact = PASS`;
- `owner_host_snapshot_restored = true`.

The final wrapper result must include:

`APL-REL-014 owner-host wrapper: PASS`

The signed production release directory is not modified.
