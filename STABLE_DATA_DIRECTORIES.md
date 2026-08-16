# APL-SEC-002 — Stable data directories

Status: **IMPLEMENTED**

Windows mutable state remains anchored under the per-user LocalAppData namespace:

`%LOCALAPPDATA%\Arvectum\ProxyLauncher`

The executable/install directory is not used for mutable Windows state. Configuration, last-known-good configuration, recovery evidence, quarantine, no-proxy state, PID/logs and recovery backups all resolve from the stable data root.

New governed paths:

- `proxy_settings.json` — active configuration;
- `proxy_settings.lastgood.json` — previous validated configuration;
- `config_recovery.json` — non-secret recovery evidence;
- `quarantine/` — structurally corrupted configuration evidence.

Tests assert that all Config & Security state is contained by the stable data directory.
