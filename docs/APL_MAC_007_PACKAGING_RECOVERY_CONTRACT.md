# APL-MAC-007 — packaging / recovery contract tests

Status: implemented and included automatically in the macOS packaging workflow.

The contract makes ownership boundaries executable:

- `.app` and DMG builders do not read, write or delete `macos_proxy_backup.json`;
- packaging does not invoke `networksetup` mutations or recovery methods;
- rollback ownership remains exclusively in `macos_backend.py`;
- LaunchAgent state is separate from rollback state and cannot alter network settings;
- DMG distribution has no installer/uninstaller hooks.

This prevents future packaging changes from quietly becoming a second network-state owner.

- [x] packaging/recovery separation asserted;
- [x] autostart/recovery separation asserted;
- [x] no installer lifecycle network hooks;
- [x] runs on macOS CI as part of `test_macos*.py`;
- [ ] real crash/reboot/restore observation — APL-MAC-008.
