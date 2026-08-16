# APL-MAC-005 — DMG packaging

Status: implemented with arm64/x64 CI construction, verification and read-only mount inspection.

`tools/build_macos_dmg.sh` packages the canonical `.app` plus the conventional `/Applications` shortcut using Apple `hdiutil`. Artifact identity includes repository version and host architecture. The script verifies the image after creation and contains no proxy, privilege or autostart mutation.

CI mounts each generated image read-only, verifies the embedded app plist and Applications symlink, then uploads the DMG together with `.app` evidence.

- [x] native Apple DMG construction;
- [x] version/architecture artifact identity;
- [x] Applications shortcut;
- [x] `hdiutil verify`;
- [x] read-only mount/content inspection on arm64 and x64 macOS 15 runners;
- [x] packaging safety contract tests;
- [ ] real Finder/install/launch acceptance — APL-MAC-008.
