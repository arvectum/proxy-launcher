# APL-LNX-008 — AppImage portable package

Status: implemented and CI-verifiable; real Astra graphical acceptance remains APL-LNX-010.

The AppImage is built from the same frozen Linux application used by the Debian package. The package creates a standards-shaped AppDir with `AppRun`, one desktop entry, a matching icon and `.DirIcon`, then invokes a hash-pinned `appimagetool` with an explicitly supplied hash-pinned type-2 runtime.

## Supply-chain boundary

`tools/appimage-toolchain.lock` records the exact appimagetool version, source/runtime provenance and SHA-256 digests. `tools/fetch_appimage_toolchain.sh` is the only network-fetch step. `tools/build_linux_appimage.sh` performs no network download and refuses a tool/runtime whose digest does not match the lock.

These are build-only dependencies; they are not required on the end-user host and are recorded for APL-IP-002-LNX.

## Safety boundary

The AppImage contains application files only. Packaging does not invoke `sudo`, PolicyKit or NetworkManager, does not change proxy state, and does not create or remove user configuration/autostart/recovery state.

## Acceptance

- [x] Standard AppDir structure with `AppRun`, desktop entry and icon.
- [x] Portable x86_64 AppImage output versioned from repository `VERSION`.
- [x] appimagetool and runtime are explicit build-only dependencies with SHA-256 verification.
- [x] Build does not rely on an implicit latest runtime download.
- [x] CI extracts and inspects the image without FUSE.
- [x] Packaging cannot mutate proxy or user state.
- [ ] Real graphical execution on Astra Linux (APL-LNX-010).
