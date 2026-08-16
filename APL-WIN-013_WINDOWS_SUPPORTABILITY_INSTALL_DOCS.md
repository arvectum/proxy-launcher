# APL-WIN-013 — Windows supportability & user-facing install docs finalization

## Status

Implemented for the Windows productization track.

## User-facing documentation set

The Windows release now has two canonical end-user entry points:

- `INSTALL.txt` — installer, upgrade, repair, uninstall, support and recovery guidance;
- `release/README_WINDOWS_PORTABLE.txt` — the README embedded in the portable ZIP.

Internal engineering milestone labels are prohibited from those packaged user-facing documents.

## Installer guidance

The recommended Windows path is the canonical per-user setup:

`Arvectum-Proxy-Launcher-X.Y.Z-windows-x64-setup.exe`

The user guide explains:

- checksum verification before execution;
- per-user install without the standard need for administrator privileges;
- stable executable path under Documents;
- persistent state under LocalAppData;
- same-user upgrade using the newer setup;
- repair through the cached `Repair Arvectum Proxy Launcher` shortcut;
- normal Windows uninstall;
- intentional preservation of persistent user configuration;
- ownership-safe handling of startup state.

## Portable guidance

The portable package README explains:

- extraction and first run;
- stable Documents handoff;
- fallback behavior if handoff is blocked;
- persistent state location;
- App Control/native QA helper scripts included in the ZIP;
- integrity and signing boundaries.

The previous P0-specific portable README is historical only and is no longer packaged by the canonical clean build.

## Supportability contract

The built executable itself exposes read-only support commands:

```text
Arvectum Proxy Launcher.exe --doctor
Arvectum Proxy Launcher.exe --doctor-json <output.json>
```

The support guide also identifies `%LOCALAPPDATA%\Arvectum\ProxyLauncher\install.log` as installation/maintenance evidence and asks the reporter to include the exact product version and package SHA-256.

Support material must not require users to publish proxy credentials, passwords, tokens or unredacted secrets. Existing Doctor/diagnostics redaction remains part of the supportability boundary.

## Recovery guidance

The final user documentation does not tell users to delete recovery state as a generic troubleshooting step. It explicitly preserves the recovery-first model:

- do not remove LocalAppData state while proxy/recovery is active;
- prefer application recovery/rollback;
- repair fails closed if safe recovery cannot be proven;
- ambiguous or foreign startup state is preserved.

## Trust/signing guidance

The documentation distinguishes Windows metadata/branding from cryptographic signing. Until the separately governed Russian production signing path is activated, users are directed to the canonical release channel and published SHA-256 evidence rather than being told that the binary is signed.

## Acceptance

APL-WIN-013 is accepted when:

1. the canonical portable build packages `release/README_WINDOWS_PORTABLE.txt`;
2. `INSTALL.txt` and the packaged portable README contain no internal P0/RC milestone labels;
3. APL-WIN-011 records PASS for all documentation presence/cleanliness checks;
4. Windows lifecycle CI passes, proving that the documented upgrade/repair/uninstall behavior matches executable behavior.
