# APL-IP-001 — platform payload / license carry-forward reconciliation

Date: 2026-08-21  
Status: **ENGINEERING RECONCILIATION COMPLETE / FINAL LEGAL APPROVAL NOT CLAIMED**

This record closes the bounded engineering portion of the pre-refactor APL-IP-001 platform/license carry-forward. It does not convert the historical review candidate into an APPROVED clean-IP baseline and does not replace human/legal review.

## Preserved baseline

- Historical APL-IP-001 review candidate: `7c3bdbd005e6ff27db8f5a00071dc81c8595dd9b`.
- Candidate tree: `9c372b440919b3b9e69d78ab0a85dca3f387d5af`.
- Build SBOM SHA-256 recorded by the candidate review packet: `fccd5d2d94a4c2f8ebbc9fdde709db5b0fd1ae13f962f9046d706086a345ac4a`.
- `requirements-build.lock.txt` is the exact repository build-dependency lock consumed by `.github/workflows/sbom.yml`.
- `THIRD_PARTY_NOTICES.txt` is the canonical human-readable distribution notice inventory.

The packaging hardening performed for this carry-forward closure is intentionally later than the preserved review candidate. It must be carried into APL-IP-003 and the new post-refactor review; it must not be presented as if it had existed in the historical candidate.

## Build SBOM boundary

The CycloneDX workflow is deliberately a **build-dependency SBOM**, not a universal final-artifact SBOM. CI generates CycloneDX 1.6 from `requirements-build.lock.txt`, validates it, and fails if any locked build dependency/version is missing or mismatched.

Repository lock set:

- `altgraph==0.17.5`
- `packaging==26.3`
- `pefile==2024.8.26`
- `pyinstaller==6.22.0`
- `pyinstaller-hooks-contrib==2026.6`
- `pywin32-ctypes==0.2.3`
- `setuptools==84.0.0`

No claim is made that this seven-component build SBOM alone enumerates every byte shipped by every platform package.

## Platform reconciliation matrix

| Platform/package | Payload boundary | Notice/license delivery | Carry-forward disposition |
|---|---|---|---|
| Windows portable ZIP | Sealed `0.2.3` portable artifact from governed Windows build | Canonical Russian-first release ceremony copies `LICENSE.txt` and `THIRD_PARTY_NOTICES.txt` beside the exact hash-bound ZIP | **RECONCILED AT RELEASE-SET LEVEL** |
| Windows Inno installer | Sealed `0.2.3` installer from Inno Setup 6.7.1 governed build | Same exact release set carries `LICENSE.txt`, `THIRD_PARTY_NOTICES.txt`, build evidence and verification UX; Inno compiler is a build tool, not represented as Arvectum source | **RECONCILED AT RELEASE-SET LEVEL** |
| Linux `.deb` | Finished Arvectum application binary + launcher + desktop entry + icon; `network-manager` stays an OS package dependency | Package script installs product `LICENSE` and `THIRD_PARTY_NOTICES.txt` under `/usr/share/doc/arvectum-proxy-launcher`; no maintainer scripts mutate proxy/user state | **RECONCILED BY PACKAGE CONTRACT** |
| Linux AppImage | Finished Arvectum application binary + AppDir metadata + separately SHA-256-pinned AppImage type-2 runtime | Carry-forward hardening now embeds product `LICENSE` and `THIRD_PARTY_NOTICES.txt` under `/usr/share/doc/arvectum-proxy-launcher` | **BOUNDED / OPTIONAL DISTRIBUTION HOLD** — see below |
| macOS `.app` | PyInstaller `.app` bundle + canonical Arvectum resources | Carry-forward hardening copies `LICENSE.txt` and `THIRD_PARTY_NOTICES.txt` into `Contents/Resources` | **RECONCILED BY PACKAGE CONTRACT; EXACT NEW ARTIFACT PROOF DEFERRED TO POST-REFACTOR BUILD** |
| macOS DMG | Exact staged `.app` + `/Applications` link; `hdiutil` is host build tooling | Carry-forward hardening also exposes `LICENSE.txt` and `THIRD_PARTY_NOTICES.txt` at DMG root | **RECONCILED BY PACKAGE CONTRACT; EXACT NEW ARTIFACT PROOF DEFERRED TO POST-REFACTOR BUILD** |

## Windows evidence binding

Canonical repository evidence records:

- `docs/evidence/WINDOWS_INNO_6_7_1_PRODUCTION_BUILD_EVIDENCE.json` — production build PASS/CLOSED, portable ZIP SHA-256 `62d313547b4d8c2c8e6951d6cd866bb954fdf199ad7650063c8ed3bfbc455801`, installer SHA-256 `5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414`.
- `docs/evidence/WINDOWS_RUSSIAN_PRODUCTION_SIGNING_ACCEPTANCE_2026-08-20.json` — exact release-set publication acceptance for tag `v0.2.3-ru.2`.
- `tools/windows_russian_production_signing.ps1` — fail-closed release ceremony requires and copies `LICENSE`, `THIRD_PARTY_NOTICES.txt` and exact build evidence into the external release directory.

This is a release-set reconciliation. It does not pretend that the build SBOM is a binary-level inventory of the frozen executable.

## Linux `.deb` boundary

`tools/build_linux_deb.sh` packages the already-built executable and explicitly installs:

- `/usr/share/doc/arvectum-proxy-launcher/copyright` from repository `LICENSE`;
- `/usr/share/doc/arvectum-proxy-launcher/THIRD_PARTY_NOTICES.txt`;
- a dependency on system `network-manager` rather than vendoring NetworkManager;
- no `postinst`, `prerm`, `postrm` or system-wide autostart mutation.

The `.deb` lane is therefore the preferred controlled Linux/Astra distribution path for the current Russian-first strategy.

## AppImage exception — bounded, not hidden

The AppImage lane uses an exact build-only tool/runtime lock:

- `APPIMAGETOOL_VERSION=1.9.1`;
- `APPIMAGETOOL_SHA256=ed4ce84f0d9caff66f50bcca6ff6f35aae54ce8135408b3fa33abfc3cb384eb0`;
- `APPIMAGE_RUNTIME_SOURCE_COMMIT=75849dce7cc37e4319b633df1f116ca895c71a12`;
- `APPIMAGE_RUNTIME_SHA256=1cc49bcf1e2ccd593c379adb17c9f85a36d619088296504de95b1d06215aebbf`.

The exact upstream runtime license at that commit is MIT for the runtime itself, but it explicitly identifies statically linked `musl libc`, `libfuse`, `squashfuse`, `libzstd` and `zlib` under their own license terms. Therefore this review **does not** turn the optional AppImage lane into an unconditional commercial-distribution PASS merely because the top-level runtime says MIT.

Carry-forward policy:

1. AppImage remains optional; `.deb` is the preferred controlled Linux/Astra package.
2. Product and third-party notices are now physically bundled in the AppImage.
3. Before an AppImage is promoted to a commercial production release, the exact runtime/transitive license texts and any source/relinking obligations must be packaged or otherwise satisfied and then human/legal-reviewed.
4. This bounded exception is not a blocker for preserving the Windows `0.2.3` baseline or for performing APL-IP-003, provided AppImage is not represented as already legally cleared.

## macOS boundary

`tools/build_macos_app.sh` builds the `.app` with PyInstaller and now places the canonical product license and third-party notices into `Contents/Resources`. `tools/build_macos_dmg.sh` stages that exact app and additionally exposes both notice files at the DMG root. `hdiutil` is used as host tooling and is not redistributed as Arvectum-authored software.

An exact post-refactor macOS artifact must still be built and rebound to the new post-refactor IP review. That future artifact proof is intentionally not fabricated here.

## PyInstaller / Python distribution note

The repository uses PyInstaller `6.22.0` in the locked build set. Upstream PyInstaller licensing includes a GPL-2.0-or-later bootloader exception that permits commercial applications to be bundled and their generated executable bundles to be shipped under the application's license, subject to the licenses of included dependencies. Python remains under the PSF License. These facts support the packaging design but do not substitute for retaining the required notices/licenses in the distributed set.

## Carry-forward conclusion

Engineering disposition:

- **PASS** — build lock ↔ build SBOM contract is explicit and CI-enforced;
- **PASS** — Windows release-set notice/evidence delivery is explicit and hash-bound;
- **PASS** — `.deb` notice delivery is explicit and test-covered;
- **PASS** — AppImage notice delivery is now explicit and test-covered;
- **PASS** — macOS `.app`/DMG notice delivery is now explicit and test-covered;
- **BOUNDED HOLD** — optional AppImage commercial-distribution clearance remains subject to its statically linked runtime/transitive-license obligations;
- **DEFERRED BY DESIGN** — exact new Linux/macOS artifact-byte reconciliation belongs to the post-refactor candidate/build, not to the immutable historical `0.2.3` evidence.

No incompatible license or unknown dependency was identified in the Arvectum-owned source inventory by the existing APL-IP-001 pre-review, but **final legal/commercial-distribution approval is not asserted by this engineering record**.
