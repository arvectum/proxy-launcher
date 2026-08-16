# APL-LNX-006 — Linux diagnostics & support bundle

Status: implemented (code/CI contract); native Astra Linux acceptance remains an environment gate.

## Goal

Provide one support-ready, privacy-bounded ZIP for Linux and Astra Linux that captures enough local state to investigate Proxy Launcher, NetworkManager, PolicyKit, autostart and rollback problems without changing the network, requesting privileges, requiring internet access, or copying credential-bearing state files.

Bundle schema:

`arvectum.proxy.linux_diagnostics.v1`

Canonical implementation:

`linux_diagnostics.py`

## Relationship to Doctor

APL-DIAG-004 Doctor and APL-LNX-006 solve different support problems.

- **Doctor** is an immediate read-only health check used by the GUI to tell the user whether action is required.
- **APL-LNX-006 support bundle** exports a bounded ZIP that can be attached to a support case and inspected later.

The collector does not replace Doctor and does not make recovery or authorization decisions.

## Collected state

`diagnostics.json` contains isolated best-effort sections for:

1. **system** — Linux/platform, kernel, architecture, Python and frozen-build facts;
2. **runtime** — APL-LNX-001 distro/Astra detection, version, desktop/session type and `nmcli` availability;
3. **application** — product version, milestone, credential-free settings summary, `no_proxy` and metadata for important application/state paths;
4. **proxy_state** — engine state, ownership-aware system-proxy state, rollback-pending state, operational capability view, resolved localhost proxy/PAC endpoints and configured listeners;
5. **networkmanager_preflight** — APL-LNX-002 readiness verdict, daemon/connectivity state, supported active profile UUIDs, proxy-property support and modification permission classification;
6. **networkmanager_profiles** — read-only active profile UUID/type/device facts and current NetworkManager proxy properties for supported non-VPN/non-loopback profiles;
7. **environment_proxy** — current-process proxy environment variables after centralized secret redaction;
8. **listeners** — local TCP probes of the configured HTTP, SOCKS5 and PAC ports on `127.0.0.1` only;
9. **network_interfaces** — interface names only;
10. **recovery** — existence/metadata of Linux rollback evidence without reading or copying its content;
11. **autostart** — APL-LNX-005 managed/conflict/enabled status without copying the XDG `.desktop` file;
12. **policykit** — whether the current child was explicitly marked interactive and the invariant that Arvectum itself does not collect PolicyKit credentials.

Current and up to three rotated `proxy_core.log` files are included under `logs/` only after line-by-line sanitization.

## Privacy minimization

APL-LNX-006 is deliberately narrower than a generic Linux system-information dump.

It does **not** collect Wi-Fi SSIDs, MAC addresses, browser history, arbitrary process lists, arbitrary files, shell history, package inventories, home-directory contents, or external IP-address discovery.

User home-directory prefixes in diagnostic path metadata are collapsed to `~` where possible.

The settings section does not serialize upstream usernames or passwords. It keeps only support-relevant endpoint host/port and boolean `username_configured` / `password_configured` flags.

## Files that are never copied

The ZIP uses an explicit allowlist. It may contain only:

- `diagnostics.json`;
- `logs/proxy_core.log`;
- `logs/proxy_core.log.1`;
- `logs/proxy_core.log.2`;
- `logs/proxy_core.log.3`.

In particular, the collector never copies raw:

- `proxy_settings.json`;
- `proxy_settings.lastgood.json`;
- `config_recovery.json`;
- `linux_proxy_backup.json`;
- `no_proxy.txt` as a file;
- `proxy_core.pid`;
- XDG autostart `.desktop` entries;
- unrelated files from the installation, data, state or home directories.

Existence and bounded metadata may be reported when diagnostically useful, but file contents remain outside the bundle.

## Secret-redaction boundary

Every persisted diagnostic structure passes through `secret_redaction.redact_value`.

Every plaintext log line passes through `secret_redaction.redact_text`; structured JSON log lines are parsed, recursively redacted and serialized again. The final log tail receives another whole-text redaction pass so multi-line secret shapes such as private-key blocks remain covered.

This covers, among other classes:

- passwords and passphrases;
- URI user-info credentials;
- bearer/basic authorization values;
- access/refresh/session tokens;
- API keys;
- cookies;
- private keys;
- sensitive CLI parameters and query parameters.

The collector is best-effort: exception text is redacted before it can enter `diagnostics.json`.

## Read-only and privilege boundary

APL-LNX-006 performs no NetworkManager mutation.

Allowed NetworkManager operations are read-only inspection surfaces already governed by APL-LNX-002/APL-CORE-004:

- list active connections;
- read proxy properties;
- query NetworkManager status/connectivity;
- query permissions.

The collector does not call `connection modify`, `device reapply`, `set_proxy`, or any recovery method.

It does not use `sudo`, `pkexec`, a password dialog, or `nmcli --ask`. The PolicyKit interactive environment marker is observed as a fact only; diagnostics never enable it.

The only socket connections initiated by APL-LNX-006 are short probes to `127.0.0.1` on Proxy Launcher’s configured local listener ports. No external network request is made.

Settings are loaded with `migrate_legacy=False`, which uses the established diagnostic read-only path and therefore does not perform legacy credential migration or corruption recovery writes.

## Best-effort failure model

Each collector section is isolated. If, for example:

- `nmcli` is absent;
- NetworkManager daemon is unavailable;
- one active profile cannot expose its proxy properties;
- an application path cannot be stat-ed;
- autostart status cannot be proven;
- a log cannot be read;

that source is represented by an unavailable/failed field or section while the rest of the bundle is still produced.

A failure to inspect state never authorizes a mutation and never converts unknown state into a successful recovery verdict.

## Output and atomicity

With no explicit output path, the bundle is written under the current user’s XDG state location:

`${XDG_STATE_HOME}/Arvectum/ProxyLauncher/diagnostics/`

when `XDG_STATE_HOME` is an absolute path, otherwise:

`~/.local/state/Arvectum/ProxyLauncher/diagnostics/`

Canonical filename:

`ArvectumProxyDiagnostics-Linux-YYYYMMDD-HHMMSSZ.zip`

The archive is created as a sibling temporary file and published with `os.replace()` only after successful ZIP completion. Temporary bundle files are removed on failure.

## CLI

On Linux/Astra from a source/support checkout:

```text
python3 linux_diagnostics.py
python3 linux_diagnostics.py /path/to/support-bundle.zip
```

The first form uses the XDG state default. The second writes to an explicit path. Non-Linux bundle creation is rejected explicitly.

Packaging/UI exposure is intentionally separate from the collector contract, matching the established Windows diagnostics architecture: the support exporter is not conflated with the GUI Doctor health-check.

## CI verification

`.github/workflows/linux-diagnostics.yml` runs the contract on Ubuntu and macOS for cross-platform import/test safety and performs a native Ubuntu no-proxy bundle smoke.

`tests/test_linux_diagnostics.py` verifies:

- Linux/Astra runtime and NetworkManager state serialization;
- use of the read-only settings path;
- absence of NetworkManager mutation calls;
- credential omission/redaction in settings, environment, NetworkManager state and logs;
- allowlisted ZIP members only;
- exclusion of raw settings, rollback and XDG autostart content;
- best-effort section failure isolation;
- non-Linux rejection;
- home-path minimization;
- atomic ZIP publication and temporary-file cleanup.

The workflow also reruns centralized redaction tests and the existing Linux runtime, NetworkManager preflight, backend and autostart regression suites.

## Acceptance criteria

- [x] Collect distro/Astra, kernel, architecture, desktop/session and application version facts.
- [x] Collect APL-LNX-002 NetworkManager readiness and permission state without mutation.
- [x] Collect read-only active NetworkManager profile/proxy state needed for support diagnosis.
- [x] Collect ownership-aware proxy/recovery state, localhost listener state and Linux autostart status.
- [x] Include current/rotated logs only after centralized secret redaction.
- [x] Never copy raw settings, rollback evidence or autostart files into the bundle.
- [x] Omit upstream username/password values from the settings summary.
- [x] Make no external network requests and request no elevated privileges.
- [x] Keep PolicyKit interaction opt-in untouched.
- [x] Survive partial diagnostic source failures.
- [x] Write the ZIP atomically with an explicit member allowlist.
- [x] Use a per-user XDG state default rather than a system directory.
- [x] Refuse bundle creation outside Linux.
- [x] Cover privacy/read-only/atomicity behavior with dedicated tests.
- [ ] Complete one native Astra Linux graphical-host support-bundle acceptance run.

## Native Astra acceptance boundary

CI cannot prove the exact state exposed by a real Astra Fly desktop and its installed NetworkManager/PolicyKit policy. Native acceptance should therefore verify one real support bundle in both idle and proxy-enabled states and confirm:

- Astra edition/version is identified correctly;
- active managed profile(s) appear without SSID/MAC leakage;
- `ready`, `auth_required` or `unavailable` matches the observed host policy;
- no PolicyKit credential prompt appears while collecting diagnostics;
- no NetworkManager profile changes occur before/after collection;
- raw rollback/autostart/settings files remain absent from the ZIP;
- the resulting bundle contains enough information to explain a forced preflight or rollback failure.
