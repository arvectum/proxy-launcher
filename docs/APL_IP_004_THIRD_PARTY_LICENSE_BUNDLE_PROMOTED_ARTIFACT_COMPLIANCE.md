# APL-IP-004 — third-party license bundle & promoted artifact compliance

Status: **ENGINEERING COMPLETE / MERGED / PROMOTED-ARTIFACT ACCEPTANCE RECORDED**  
Date: 2026-08-22

## Purpose

APL-IP-004 remediates Finding L-1 from the post-refactor APL-IP-001 review: a human-readable `THIRD_PARTY_NOTICES.txt` inventory is not, by itself, a sufficient promoted-artifact compliance package when the licenses/copyright notices of runtime components frozen into a desktop artifact must be preserved with distribution.

This task makes complete third-party license-text delivery an explicit, fail-closed property of the promoted artifact rather than an optional release-directory convention.

This is an engineering/compliance control, not a legal opinion and not a substitute for authorized human/legal approval.

## Canonical bundle

`tools/third_party_license_bundle.py` builds a `THIRD_PARTY_LICENSES/` directory from the **exact selected build environment**. It does not download license text and does not maintain hand-copied version-independent license prose in Arvectum source.

The collector currently requires complete non-empty license/copyright texts for:

1. CPython / Python runtime;
2. Tcl;
3. Tk;
4. PyInstaller / its distributed licensing material.

The generated `manifest.json` uses schema `arvectum.third-party-license-bundle.v1` and records:

- required component family;
- original source basename;
- bundle-relative path;
- SHA-256 of every copied text;
- build Python version and platform.

Verification fails closed if a required family is absent, a file is empty/missing, the schema is wrong, or a recorded hash does not match.

## Promoted artifact rule

A frozen desktop artifact is not eligible for commercial promotion merely because the repository contains licensing documents. The applicable package/release lane must physically carry:

- Arvectum product `LICENSE` (normally exposed as `LICENSE.txt` or Debian `copyright`);
- canonical `THIRD_PARTY_NOTICES.txt`;
- generated and verified `THIRD_PARTY_LICENSES/manifest.json`;
- every complete third-party license/copyright text referenced by that manifest.

The bundle must be generated from the environment used for the frozen payload. Replacing it with manually authored summaries does not satisfy this control.

## Platform contracts

### Windows portable ZIP

`.github/workflows/windows-p0.yml` runs `tools/windows_promoted_license_compliance.ps1` after the canonical clean build. The gate:

- generates the exact bundle with the canonical `.build-venv` Python;
- embeds `LICENSE.txt`, `THIRD_PARTY_NOTICES.txt` and `THIRD_PARTY_LICENSES/` into the portable ZIP;
- re-expands and verifies the final ZIP;
- recomputes the promoted ZIP SHA-256;
- rewrites `out/SHA256SUMS.txt` and the `zip_sha256` field in `out/build-result.json` so downstream evidence binds the post-compliance bytes.

### Windows installer

`tools/build_windows_installer.ps1` requires the compliant canonical portable ZIP and copies its verified `THIRD_PARTY_LICENSES/` into the installer payload. `installer/ArvectumProxyLauncher.iss` compiles the product license, canonical notices and full third-party bundle into Setup and installs them under the Arvectum application directory.

The installer build manifest records the SHA-256 of `THIRD_PARTY_LICENSES/manifest.json`.

### Debian `.deb`

`tools/build_linux_deb.sh` builds and verifies the exact bundle and installs it at:

`/usr/share/doc/arvectum-proxy-launcher/THIRD_PARTY_LICENSES/`

The existing Debian product-license and third-party-notice delivery remains intact.

### macOS `.app` and DMG

`tools/build_macos_app.sh` builds and verifies the bundle under:

`Arvectum Proxy Launcher.app/Contents/Resources/THIRD_PARTY_LICENSES/`

`tools/build_macos_dmg.sh` requires that verified app bundle and also exposes the same bundle at the DMG root alongside `LICENSE.txt` and `THIRD_PARTY_NOTICES.txt`.

### Linux AppImage

The common Python/Tcl/Tk/PyInstaller bundle is embedded under the AppImage documentation tree, but **APL-IP-004 does not clear AppImage for promoted commercial distribution**.

The existing APL-IP-001 Finding L-2 remains in force: the pinned type-2 AppImage runtime includes statically linked third-party components (including the separately licensed libfuse path), and the exact runtime/transitive obligations require a dedicated downstream compliance bundle/review before commercial promotion.

Therefore AppImage remains **EXCLUDED FROM PROMOTED COMMERCIAL SCOPE** until a separate explicit clearance task closes L-2. Debian `.deb` remains the preferred controlled Linux/Astra distribution lane.

## Fail-closed invariants

Promotion/build must fail when any of the following is true:

- required third-party license family is not discoverable in the exact build environment;
- collected text is missing or empty;
- bundle manifest is absent or malformed;
- a license-text SHA-256 differs from the manifest;
- Windows portable artifact lacks product license, canonical notices or verified bundle;
- Windows installer cannot bind to the compliant portable bundle;
- macOS DMG is built from an app lacking the verified bundle;
- an AppImage is represented as commercially cleared merely because the common desktop bundle exists.

## Tests

`tests/test_apl_ip_004_license_compliance.py` protects:

- positive manifest/hash verification;
- tamper rejection;
- missing-component rejection;
- Windows portable promotion gate presence;
- Windows installer bundle inclusion contract;
- Debian bundle placement;
- macOS app/DMG bundle placement;
- preservation of the AppImage commercial hold.

Platform packaging workflows remain the authoritative integration acceptance because they exercise the real build environments.

## Acceptance evidence

The final APL-IP-004 implementation was merged as PR #167. The final PR head, PR test-merge and merge candidate resolve to the identical file tree `98a09d821470a597715696e5ff3c7f376e5893a8`.

Accepted candidate-equivalent packaging lanes:

- Windows portable: workflow `32556717827` — **SUCCESS**, including explicit `APL-IP-004 promoted portable license gate`;
- Windows installer: workflow `32556717718` — **SUCCESS after explicit rerun of the concurrency-cancelled job**, including installer compile, fresh/upgrade/repair/uninstall lifecycle and Gate R6 acceptance;
- Debian `.deb`: workflow `32556717706` — **SUCCESS** on Ubuntu 22.04 and 24.04, with generated/verified license bundle present in package payload;
- macOS `.app`/DMG: workflow `32556717755` — **SUCCESS** on Apple Silicon and Intel, with generated/verified bundle and DMG integrity inspection;
- AppImage: engineering packaging remains available, but commercial promotion remains **EXCLUDED / HOLD** under L-2.

Canonical exact candidate/evidence reconciliation:

`docs/evidence/APL_IP_001_POST_IP_004_CANDIDATE_RECONCILIATION_2026-08-22.md`

## Acceptance criteria

APL-IP-004 is engineering-complete because:

1. the unit/contract control is present and green in the accepted implementation matrix;
2. Windows portable build is green with the post-build promotion gate;
3. Windows installer lifecycle/packaging CI is green with embedded licensing payload;
4. Debian packaging CI is green with the generated bundle;
5. macOS `.app`/DMG packaging CI is green on supported runner architectures;
6. AppImage continues to state and enforce the L-2 promotion exclusion;
7. no historical release/provenance evidence was rewritten to claim that historical artifacts contained controls introduced later by APL-IP-004.

## Resulting disposition

Finding L-1 is **ENGINEERING-REMEDIATED for newly built promoted Windows portable, Windows installer, Debian `.deb`, and macOS `.app`/DMG artifacts**. Historical artifacts remain historical evidence and are not retroactively relabeled. Final clean-IP/commercial approval remains subject to the separate human/legal/chain-of-title gates recorded by APL-IP-001.
