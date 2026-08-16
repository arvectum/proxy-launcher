# APL-DIAG-003 — Windows diagnostics collector

**Status:** IMPLEMENTED / READY FOR MERGE  
**Depends on:** APL-DIAG-001 Structured logging, APL-DIAG-002 Secret redaction  
**Bundle schema:** `arvectum.proxy.windows_diagnostics.v1`

## Goal

Produce one support-ready Windows diagnostics ZIP that captures enough local state to investigate Proxy Launcher failures without modifying network configuration, requiring a working proxy, or leaking credentials.

## Architecture

`windows_diagnostics.py` is a dependency-free, read-only collector built on the existing `proxy_core` state model and the centralized APL-DIAG-002 redaction layer.

The collector is deliberately best-effort. Each source is isolated as its own section: a failed registry read, unavailable PowerShell/CIM query, malformed state file, or listener probe becomes an `ok: false` diagnostic section and does not prevent the remaining bundle from being created.

The final ZIP is written to a temporary sibling file and atomically renamed only after successful ZIP creation. By default it is stored under the per-user data directory in `diagnostics/ArvectumProxyDiagnostics-<UTC timestamp>.zip`.

## Collected state

`diagnostics.json` includes:

- Windows/platform, architecture, hostname and Python/frozen-runtime information;
- Proxy Launcher version, engineering milestone and important application/data paths;
- sanitized effective settings and `no_proxy` entries;
- engine/PAC/recovery/migration/orphaned-PAC state;
- WinINET Internet Settings state;
- process-level and HKCU proxy environment variables;
- configured localhost HTTP/SOCKS5/PAC listener probes;
- local network interfaces, addresses, subnets, default gateways, DNS and DHCP data via local Windows CIM, with non-resolving fallback metadata;
- backup/recovery state and recovery-autostart classification.

When present, current and rotated `proxy_core.log` files are added under `logs/` after every line is sanitized again before it enters the archive.

## Privacy and safety boundary

- No external network request is performed by the collector.
- Listener probes connect only to `127.0.0.1` and only to the three configured Proxy Launcher ports.
- Raw `proxy_settings.json`, recovery backup files and other credential-bearing state files are never copied into the ZIP.
- Every serialized data structure passes through `secret_redaction.redact_value`.
- Every raw/legacy log line passes through `secret_redaction.redact_text`.
- Structured log lines are parsed, recursively redacted and re-serialized.
- URI credentials, tokens, passwords, auth headers, cookies, DPAPI credential fields and other APL-DIAG-002 secret classes therefore remain outside the support bundle.
- Diagnostics are read-only with respect to WinINET, environment variables, Run entries and network state.

## CLI

On Windows:

```text
python windows_diagnostics.py
python windows_diagnostics.py C:\path\to\support-bundle.zip
```

The first form writes to the default per-user diagnostics directory. The second writes to the requested ZIP path. Non-Windows bundle creation is rejected explicitly; platform-neutral unit tests can still exercise the collector with mocked Windows state.

## Acceptance criteria

- [x] Collect Windows/application version and relevant application paths.
- [x] Collect network interfaces without external connectivity.
- [x] Collect WinINET proxy state and process/HKCU proxy environment state.
- [x] Probe configured HTTP, SOCKS5 and PAC listeners on localhost only.
- [x] Collect recovery backups, migration state and recovery-autostart classification.
- [x] Include current/rotated structured logs in sanitized form.
- [x] Never copy raw credential-bearing settings or backup files into the archive.
- [x] Apply the centralized APL-DIAG-002 redaction layer to every persisted diagnostic value.
- [x] Survive partial source failures and still produce the remaining snapshot/bundle.
- [x] Work when the engine is stopped and recovery is pending after an interrupted session.
- [x] Create the ZIP atomically and clean temporary files after success/failure.
- [x] Refuse Windows bundle creation on non-Windows systems.
- [x] Run dedicated collector/privacy tests on Ubuntu and Windows in GitHub Actions.
- [x] Run a native Windows no-proxy support-bundle smoke test in GitHub Actions.
