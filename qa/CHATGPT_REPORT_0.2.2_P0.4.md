# Arvectum Proxy Launcher for Windows — QA report 0.2.2 P0.4

## Final result

`RESULT: PASS`

`CUSTOMER UPDATE INSTALLER: APPROVED`

`AUTHENTICODE: NOT SIGNED`

## Delivered package

- Customer package: `Arvectum-Proxy-Launcher-Windows-0.2.2-P0.4-client.zip`.
- Application EXE: `Arvectum Proxy Launcher.exe`.
- Application version: `0.2.2.0`.
- Application EXE SHA256: `7EF02652E31BBBD68833BE599135CF59519C42B1F8A8FEBB580B3891FFC35EC0`.
- Default diagnostic URL: `https://arvectum.com`.

## Source and tests

- Application production code changed: YES — only the GUI default diagnostic
  URL changed from `https://api.ipify.org` to `https://arvectum.com`.
- Proxy transport, PAC routing, DPAPI, no_proxy, stable state location and
  rollback logic were not changed for P0.4.
- Installer/update layer changed: active legacy recovery migration, strict
  ownership classification, controlled legacy shutdown, UTF-8 batch setup and
  PowerShell diagnostic wrapper.
- Python compile and PowerShell parser checks: PASS.
- Automated regression suite: `77/77 PASS`.

## P0.4 mandatory native QA

### Active legacy recovery customer fixture

- Legacy recovery Run entry classified as proven Arvectum: PASS.
- Legacy recovery process active before installation: PASS.
- Exact legacy process identified and stopped by its own `--stop`: PASS.
- Legacy network recovery completed: PASS.
- Legacy process exited: PASS.
- Legacy recovery Run entry removed: PASS.
- Legacy user autostart migrated to canonical install: PASS.
- Source/staged/installed hash verification: PASS.
- Three listeners (`8080`, `1080`, `8082`) stayed active after 16 seconds: PASS.
- Stop exact WinINET/environment rollback: PASS.
- Proxy resumed after QA: PASS.

### Remaining safety gates

- Missing legacy Temp EXE: stale proven Run entry removed; update completed: PASS.
- Active foreign recovery Run/process: Run entry and process preserved; update
  blocked; installed EXE unchanged: PASS.
- Open canonical GUI: only exact canonical process closed; update completed and
  installed hash verified: PASS.

## Security properties

- Active processes are acted on only after exact executable path, known legacy
  path/archive pattern and expected `--start` arguments are verified.
- Unknown or foreign recovery Run commands are never stopped, removed or
  overwritten; installation returns non-zero.
- If graceful legacy stop, process exit or recovery backup removal cannot be
  proven safe, update is blocked and the previous EXE is retained.
- Upstream credentials use Windows DPAPI; the package contains no credentials,
  settings, PID files, recovery backups or logs.

## Customer installation

1. Extract the ZIP into a dedicated folder.
2. Run `install.bat`.
3. Open the desktop shortcut, configure the upstream and enable proxy.
4. Use **Check connection** before enabling Windows autostart.

If installation is blocked, provide:
`%LOCALAPPDATA%\Arvectum\ProxyLauncher\install.log`.
