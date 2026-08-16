# APL-MAC-001 — macOS runtime & read-only preflight model

Status: implemented in source/tests; real host acceptance remains APL-MAC-008.

`macos_runtime.py` detects the darwin runtime, product version, architecture and availability of the Apple system tools used by later packaging/autostart work. `macos_networksetup_preflight.py` performs only read operations through `networksetup`: it enumerates enabled network services and verifies that the automatic-proxy and bypass-domain state is readable before mutation is considered safe.

The preflight is explicitly fail-closed. Missing `networksetup`, no enabled services, unreadable proxy state or an authorization boundary are represented as capability states rather than guessed support. No proxy/network setting is changed by detection.

- [x] deterministic darwin-only runtime model;
- [x] Apple system-tool availability recorded;
- [x] enabled-service detection;
- [x] PAC/bypass readability probe;
- [x] ready/auth-required/unavailable result model;
- [x] injected runner tests with no host mutation;
- [ ] real macOS host observation — APL-MAC-008.
