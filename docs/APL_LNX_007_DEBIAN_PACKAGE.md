# APL-LNX-007 — Debian package (.deb)

Status: implemented in repository/CI; real Astra installation acceptance is tracked by APL-LNX-010.

## Goal

Produce a conventional Debian-family package for Arvectum Proxy Launcher without weakening the existing ownership, rollback, PolicyKit or per-user state boundaries.

## Package contract

`tools/build_linux_deb.sh` consumes the frozen PyInstaller Linux artifact and creates:

`dist/deb/arvectum-proxy-launcher_<VERSION>_<arch>.deb`

Installed system payload:

- `/opt/arvectum-proxy-launcher/Arvectum Proxy Launcher` — frozen application;
- `/usr/bin/arvectum-proxy-launcher` — stable launcher wrapper;
- `/usr/share/applications/arvectum-proxy-launcher.desktop` — desktop registration;
- `/usr/share/icons/hicolor/256x256/apps/arvectum-proxy-launcher.png` — application icon;
- `/usr/share/doc/arvectum-proxy-launcher/copyright` — project license;
- `/usr/share/doc/arvectum-proxy-launcher/THIRD_PARTY_NOTICES.txt` — bundled dependency notices.

The package declares `network-manager` because the governed Linux/Astra backend is NetworkManager/nmcli-based.

## Safety boundary

The `.deb` deliberately contains no `postinst`, `prerm` or `postrm` scripts. Installing, upgrading or removing the package therefore does not:

- enable/disable a proxy;
- call `nmcli connection modify`;
- trigger PolicyKit;
- create system-wide autostart;
- delete per-user settings, credentials, diagnostics or rollback evidence;
- delete user-owned XDG autostart state.

Autostart remains the explicit per-user APL-LNX-005 function. Proxy restoration remains owned by the runtime recovery state machine, not by dpkg maintainer hooks.

## Reproducibility and provenance

- Version comes only from repository `VERSION`.
- Architecture comes from `dpkg --print-architecture`, with an explicit `DEB_ARCH` override for controlled packaging jobs.
- `SOURCE_DATE_EPOCH` is honored and defaults to the source commit timestamp.
- `dpkg-deb --root-owner-group` normalizes archive ownership.
- Package contents include the repository license and third-party notices.

## CI acceptance

`.github/workflows/linux-deb.yml` builds the frozen app and package on supported Ubuntu runners, executes unit/contract tests, inspects package metadata and extracts the package into an isolated root for payload verification. No root installation and no host proxy mutation are required for CI acceptance.

## Acceptance criteria

- [x] Build a valid `.deb` from the canonical Linux frozen artifact.
- [x] Use a stable package/application/launcher identity.
- [x] Register a desktop entry and icon.
- [x] Include license and third-party notices.
- [x] Declare the NetworkManager runtime dependency.
- [x] Contain no package lifecycle hook capable of changing network or user state.
- [x] Preserve per-user configuration/recovery/autostart across package removal.
- [x] Make version/architecture/provenance deterministic and inspectable.
- [x] Verify package structure on Ubuntu CI.
- [ ] Install/upgrade/remove the package on one real Astra Linux graphical host (APL-LNX-010).
