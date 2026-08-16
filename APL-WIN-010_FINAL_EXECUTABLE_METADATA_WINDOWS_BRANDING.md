# APL-WIN-010 — Final executable metadata & Windows branding

## Status

Implemented for the Windows `0.2.3` productization track.

## Objective

Make the Windows application and installer identify themselves consistently as an Arvectum product without relying on hand-maintained version resources.

## Canonical metadata source

`VERSION` is the only product-version source of truth. `tools/generate_windows_version_info.py` converts the SemVer value into the Windows numeric `MAJOR.MINOR.PATCH.0` resource tuple while preserving the canonical SemVer string as `ProductVersion`.

The canonical build regenerates `version_info.txt` before PyInstaller runs. A stale checked-in version resource therefore cannot silently brand a newly built executable with the wrong product version.

## Application executable contract

The final `Arvectum Proxy Launcher.exe` must expose:

| Field | Required value |
|---|---|
| CompanyName | `ООО «Арвектум»` |
| ProductName | `Arvectum Proxy Launcher` |
| FileDescription | `Arvectum Proxy Launcher` |
| ProductVersion | canonical `VERSION` |
| FileVersion | `MAJOR.MINOR.PATCH.0` |
| InternalName | `ArvectumProxyLauncher` |
| OriginalFilename | `Arvectum Proxy Launcher.exe` |
| Copyright | `© 2026 ООО «Арвектум». All rights reserved.` |
| Icon | `assets/arvectum.ico` |

`tools/clean_build_windows.ps1` reads the metadata back from the **final built PE file** and fails the build if the required values do not match.

## Installer branding contract

The canonical Inno Setup installer is `installer/ArvectumProxyLauncher.iss`. Its user-visible identity is:

- product: `Arvectum Proxy Launcher`;
- publisher/company: `ООО «Арвектум»`;
- description: `Arvectum Proxy Launcher Windows Installer`;
- product version: canonical `VERSION`;
- numeric Windows version: `MAJOR.MINOR.PATCH.0`;
- publisher URL: `https://arvectum.com`;
- support URL: the canonical GitHub issue tracker;
- installer icon: `assets/arvectum.ico`.

`tools/build_windows_installer.ps1` verifies the final setup PE metadata after Inno Setup compilation.

## Trust boundary

Windows branding metadata and the product icon identify the binary but **do not constitute a digital signature**. Production embedded signing remains governed by `RELEASE_POLICY.md`, `release/APL_REL_009_RUSSIAN_PRODUCTION_SIGNING_ARCHITECTURE.md`, and `release/APL_REL_010_RUTOKEN_CRYPTOPRO_SIGNING_POC.md`.

Gate R6 must not claim that the Windows binaries are production-signed until that separate signing track is explicitly activated.

## Acceptance evidence

APL-WIN-010 is accepted when:

1. the canonical Windows build succeeds;
2. the application PE metadata checks in `tools/clean_build_windows.ps1` pass;
3. the setup PE metadata checks in `tools/build_windows_installer.ps1` pass;
4. `tools/windows_rc_acceptance.ps1` records PASS for all executable and setup branding checks.
