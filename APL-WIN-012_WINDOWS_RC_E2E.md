# APL-WIN-012 — Windows RC smoke / upgrade / repair / uninstall end-to-end

## Status

Implemented as `qa/windows_rc_e2e.ps1` and intended to run on the Windows CI runner against the exact RC installer bytes.

## Purpose

Prove the complete Windows product lifecycle instead of treating build success or a fresh-install smoke test as sufficient productization evidence.

## E2E phases

### 1. Fresh install and smoke

The current RC setup is installed silently on a clean runner-owned application/state path. The harness verifies:

- the installed executable exists;
- the cached repair setup exists;
- final PE company/product/version metadata match the current `VERSION`;
- `Arvectum Proxy Launcher.exe --status` exits successfully;
- `install.log` records `PASS (INSTALL)`.

The fresh installation is then uninstalled successfully.

### 2. Upgrade

CI installs an explicitly marked **synthetic predecessor** setup before the current RC. The predecessor carries a previous installer manifest version so the maintenance path is forced through a real version transition.

Before upgrade, the harness writes valid persistent `proxy_settings.json` and `no_proxy.txt` fixtures and records their SHA-256 hashes. The current setup must then:

- classify the operation as `UPGRADE` rather than `REPAIR`;
- replace the application transactionally;
- install the current non-synthetic manifest;
- execute `--status` successfully;
- preserve both persistent configuration hashes exactly.

The synthetic predecessor is lifecycle test infrastructure only. Its application payload may come from the current build; therefore this phase proves the **installer upgrade state machine and persistence invariants**, not historical backward compatibility with every previously released executable.

### 3. Repair

The harness deliberately damages the installed executable and seeds stale Arvectum-owned `.new`, `.old`, PID, and recovery-autostart artifacts. Running the cached repair setup must:

- classify the operation as `REPAIR`;
- restore the exact current executable and metadata;
- remove stale owned operational artifacts;
- keep persistent configuration byte-for-byte unchanged;
- make `--status` succeed again.

### 4. Uninstall

Before uninstall, the harness seeds:

- an Arvectum-owned main startup entry;
- a foreign value using the recovery-entry name;
- the persistent configuration from the upgrade phase.

Uninstall must remove the application/cached repair setup and the provably owned main startup entry while preserving the foreign startup value and persistent configuration.

## Evidence

A successful run writes `out/windows-rc-e2e.json` with schema `arvectum.proxy.windows-rc-e2e.v1` and PASS values for:

- `fresh_install_smoke`;
- `fresh_uninstall`;
- `upgrade`;
- `repair`;
- `uninstall`;
- configuration preservation;
- foreign startup preservation.

APL-WIN-011 consumes this file. Gate R6 cannot pass if this lifecycle evidence is absent or non-PASS.

## Safety boundary

The E2E harness is destructive only inside the runner/current-user paths owned by Arvectum Proxy Launcher and the specifically named HKCU startup values used by the test. It must not be run casually on a workstation with an active production proxy session.
