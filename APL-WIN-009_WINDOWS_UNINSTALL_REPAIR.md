# APL-WIN-009 — Windows uninstall/repair flow and stale-state cleanup

Status: **implemented**

## Goal

Provide a production-safe Windows maintenance lifecycle for Arvectum Proxy Launcher: a recoverable repair path for damaged installations, a fail-closed uninstall path when network recovery is incomplete, and cleanup of stale runtime/install artifacts without deleting persistent user configuration or touching foreign Windows startup state.

## Repair flow

The canonical Inno Setup executable is also the repair mechanism. After every successful install/repair, Setup caches itself as:

`%USERPROFILE%\Documents\ArvectumProxyLauncher\Arvectum Proxy Launcher Repair.exe`

A Start-menu entry named `Repair Arvectum Proxy Launcher` launches that cached Setup. Re-running a newer downloaded Setup follows the same repair-safe path and refreshes the cached repair copy after success.

Repair behavior:

1. Embedded application and helper SHA-256 values are verified before replacement.
2. If recovery backups exist, the currently installed Launcher must still be available and must complete its own `--stop` rollback before repair continues.
3. If recovery backups exist but the installed Launcher is missing or cannot complete rollback, repair is **fail-closed** and does not delete the backups.
4. If no recovery backups exist, a missing or damaged application EXE is repairable; Setup does not require executing the damaged EXE first.
5. Application replacement remains transactional through `.new` / `.old` staging and rollback.
6. After a successful replacement, repair removes only stale operational artifacts: stale `.new` / `.old`, a dead/mismatched `proxy_core.pid`, and an owned stale `ArvectumProxyLauncherRecovery` Run value.
7. Persistent user configuration is preserved. Repair does not remove `proxy_settings.json`, `no_proxy.txt`, or maintenance logs.

## Uninstall flow

The installed Inno uninstaller invokes the installed `uninstall_helper.ps1` before destructive removal.

Uninstall behavior:

1. If recovery backups exist, the application must complete `--rollback` successfully before uninstall is permitted.
2. If recovery backups exist but the application EXE is missing, uninstall is blocked. Recovery files are retained for manual/support recovery rather than silently abandoning network state.
3. Only running `Arvectum Proxy Launcher.exe` processes whose resolved executable path exactly matches the installation are terminated.
4. The per-user Run values `ArvectumProxyLauncher` and `ArvectumProxyLauncherRecovery` are removed only when they exactly target this installation with `--start`.
5. A legacy scheduled task named `ArvectumProxyLauncher` is removed only when an actual `<Exec>` action exactly targets this installation with `--start`. A same-named foreign/unknown task is preserved.
6. Stale `proxy_core.pid` is removed after owned processes are stopped.
7. The cached repair Setup and transactional `.new` / `.old` files are removed with the installed payload.
8. Persistent state under `%LOCALAPPDATA%\Arvectum\ProxyLauncher` is intentionally retained, including `proxy_settings.json` and `no_proxy.txt`, so uninstall/reinstall does not silently destroy the user's proxy configuration. This can be revisited later as an explicit "remove user data" UX option rather than being implicit.

## Ownership and safety boundaries

APL-WIN-009 preserves the existing Arvectum ownership rules:

- no global process-name killing;
- no unconditional deletion of same-named registry values or scheduled tasks;
- no manual deletion of recovery backup files as a substitute for successful rollback;
- no recursive deletion outside the Inno-owned installation directory;
- foreign or ambiguous startup state is left untouched.

## CI / regression evidence

`tests/test_windows_maintenance_flow.py` fixes the maintenance contract in source-level regression tests.

The Windows installer workflow performs a real lifecycle smoke on `windows-latest`:

- fresh install;
- confirmation that the cached repair Setup exists;
- creation of persistent configuration sentinels;
- creation of stale `.new`, `.old`, stale PID, and owned recovery Run state;
- deliberate corruption of the installed application EXE;
- repair from the cached Setup;
- verification that the repaired EXE runs and stale operational state is gone;
- verification that persistent configuration remains unchanged;
- uninstall with an owned main Run value plus a foreign same-named recovery value;
- verification that owned state is removed, foreign state is preserved, and persistent configuration survives uninstall.

Full repository regression and Windows installer CI are required before merge.
