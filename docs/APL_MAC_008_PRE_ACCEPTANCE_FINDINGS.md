# APL-MAC-008 — pre-acceptance integration findings

Status: **MUST RESOLVE / VERIFY BEFORE REAL-HOST PASS**

These findings were identified while preparing the real macOS acceptance gate. They are not grounds for waiving a test. APL-MAC-008 / Gate R9 remains open until the exact release candidate resolves or disproves each relevant finding on a real Mac.

## F1 — shared GUI still contains Windows-only autostart and recovery UX

`macos_autostart.py` implements the canonical APL-MAC-006 LaunchAgent contract, but the current shared GUI still exposes Windows-specific autostart wording and Windows Registry / Task Scheduler handlers.

Required before PASS:

- Darwin GUI uses `macos_autostart.is_autostart_enabled`, `enable_autostart`, and `disable_autostart`;
- no Registry / `schtasks` path executes on Darwin;
- autostart wording is macOS-correct;
- recovery wording refers to macOS/system network settings rather than Windows;
- Windows 0.2.3 behavior and regression tests remain unchanged;
- deterministic tests cover platform dispatch and prevent regression.

## F2 — mutable runtime state currently inherits the legacy non-Windows install directory

The runtime facade preserves the legacy core object. In `proxy_core_legacy.py`, `data_dir()` uses Windows LocalAppData only on Windows and returns `install_dir()` on every other platform. A frozen macOS build therefore risks resolving settings, `no_proxy`, PID/log and related mutable state inside the installed `.app` bundle rather than the governed per-user Application Support location.

That is unacceptable for update/remove acceptance and can create write-permission or state-preservation failures.

Required before PASS:

- Darwin mutable state resolves to `~/Library/Application Support/Arvectum/ProxyLauncher`;
- settings, `no_proxy`, PID/log and runtime state do not live inside `/Applications/Arvectum Proxy Launcher.app`;
- the existing macOS rollback path remains in the same governed Application Support tree;
- migration from a historical valid state location preserves user data and never destroys ambiguous recovery evidence;
- Windows behavior remains byte/contract compatible and Linux behavior is not accidentally changed;
- deterministic tests prove the Darwin path and update-state preservation boundary.

Prefer the smallest platform-composition change rather than forking the legacy core wholesale.

## F3 — real `networksetup` mutation authorization must be proven, not assumed

APL-MAC-001 proves the read-only `networksetup` surface. The production backend then executes the setters directly. The real Mac acceptance must prove what happens for the actual interactive user and current macOS security policy.

Required before PASS:

- first exercise a real setter through the product as the normal logged-in user;
- never obtain PASS by launching the entire application as root;
- never store a macOS password or proxy credential as an authorization workaround;
- if macOS requires authorization, the product must surface an explicit, truthful authorization flow and leave password ownership with macOS;
- denial/failure must leave the network unchanged or safely restored from durable ownership evidence;
- no `sudo networksetup` shortcut may be treated as product acceptance.

If the exact candidate cannot mutate safely under the supported user model, classify the phase as FAIL and remediate before Gate R9 closure.

## F4 — legacy `install.command` is not the canonical APL-MAC-008 install path

The root legacy installer uses a different Application Support directory and a historical `com.arvectum.proxylauncher` LaunchAgent. The current product contract uses the APL-MAC-004/005 `.app` + DMG path and `ru.arvectum.proxylauncher`.

Required before PASS:

- install/test from the canonical `.app`/DMG candidate in `/Applications`;
- do not use legacy `install.command` as evidence for APL-MAC-008;
- final cleanup proves the canonical flow did not introduce the legacy LaunchAgent.

## Gate discipline

Resolve F1 and F2 in code before deliberate real network mutation. Resolve or empirically classify F3 during the real-host mutation phase. Keep F4 excluded from the canonical acceptance path.

Only a clean candidate commit with passing automated tests plus the real-host acceptance matrix may close Gate R9.
