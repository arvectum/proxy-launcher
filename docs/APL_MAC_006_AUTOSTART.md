# APL-MAC-006 — LaunchAgent / per-user autostart

Status: implemented/tested; real login-session acceptance remains APL-MAC-008.

Autostart is owned as one per-user LaunchAgent at `~/Library/LaunchAgents/ru.arvectum.proxylauncher.plist`. It points to the canonical `/Applications/Arvectum Proxy Launcher.app` executable, starts once at login (`RunAtLoad=true`) and is not kept alive.

The implementation deliberately does not install a daemon, root LaunchDaemon, privileged helper or system-wide startup item. Creation is atomic and mode 0600; disable removes only the Arvectum-owned plist. No proxy state is changed by enabling/disabling autostart.

- [x] stable LaunchAgent label/path;
- [x] canonical installed-app executable target;
- [x] per-user only, no root/system daemon;
- [x] atomic 0600 plist creation;
- [x] idempotent detection/removal;
- [x] deterministic tests;
- [ ] verify launch on a real Aqua login session — APL-MAC-008.
