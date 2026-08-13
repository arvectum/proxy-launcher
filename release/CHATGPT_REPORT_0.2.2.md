# Arvectum Proxy Launcher for Windows — QA report 0.2.2

## Result

`RESULT: PASS`

`CUSTOMER RELEASE: APPROVED`

`AUTHENTICODE: NOT SIGNED`

## Delivered build

- Product: Arvectum Proxy Launcher for Windows 0.2.2.
- EXE: `Arvectum Proxy Launcher.exe`.
- Application EXE SHA256: `BA66908EDB73175AC51221A82F817A4C41BDB07AD65998E4244916DF242BF780`.
- File/Product version: `0.2.2.0` / `0.2.2`.
- New multi-resolution Arvectum icon is embedded in the EXE and used by the
  desktop shortcut.

## Verification summary

- Python compile check: PASS.
- Automated regression suite: `71/71 PASS`.
- Windows GUI EXE build: PASS.
- Active update to 0.2.2: PASS; three local listeners opened (`8080`, `1080`,
  `8082`).
- Previous P0.3 installer QA: PASS — verified staging/hash replacement,
  exact-path GUI closure, legacy recovery/autostart migration, foreign Run
  value protection, blocked unsafe upgrade, exact network rollback and proxy
  restart.
- Proxy transport QA: HTTP proxy, HTTPS CONNECT and SOCKS5: PASS.
- Customer-facing release archive contains only the EXE, installer, uninstaller,
  recovery helper and documentation; no source code, tests, logs or credentials.

## Security and recovery behavior

- Upstream credentials are protected using Windows DPAPI; no plaintext
  credentials are stored in settings.
- Persistent settings, logs and recovery data are in
  `%LOCALAPPDATA%\Arvectum\ProxyLauncher`.
- The installed EXE is in
  `%USERPROFILE%\Documents\ArvectumProxyLauncher`.
- Unsafe network recovery or ambiguous ownership blocks destructive actions;
  backup files are retained for safe recovery.

## Customer instruction

1. Extract the customer ZIP into a separate folder.
2. Run `install.bat`.
3. Open the desktop shortcut, configure the upstream proxy and select
   **Enable proxy**.
4. Use **Check connection** before enabling Windows autostart.

If a recovery message appears, follow the action offered in the Launcher; do
not delete recovery files manually.
