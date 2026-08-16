# APL-IP-002-WIN — Windows stack & dependency sovereignty audit

**Status:** COMPLETE — CONDITIONAL PASS  
**Audit date:** 2026-08-16  
**Scope:** Windows x64 portable/runtime, Windows installer path, build/release/signing toolchain, dependency acquisition and source/CI continuity.

## 1. Purpose

This audit establishes the current sovereignty posture of the Windows edition of Arvectum Proxy Launcher and identifies dependencies that can prevent ООО «Арвектум» from building, releasing, supporting, or operating the Windows product if foreign package repositories, SaaS CI, vendors, or distribution endpoints become unavailable.

For this audit, **sovereign** means that Arvectum can reproduce and operate the Windows product from controlled source and pre-verified artifacts without requiring live access to foreign SaaS/package endpoints. It does **not** mean that every underlying component must be Russian-made. Windows itself is treated as an explicit platform dependency of the Windows SKU.

## 2. Executive verdict

| Area | Status | Verdict |
|---|---|---|
| End-user runtime | GREEN | Small external dependency surface; packaged app is effectively self-contained and can operate without Python/PyPI installed on the target PC. |
| Python application dependencies | GREEN | Windows application code uses Python standard library/Tkinter plus Arvectum-owned modules; no mandatory third-party PyPI application framework is imported by the Windows GUI entry point. |
| Build toolchain | AMBER | Exact versions are pinned, but the canonical build installs them live from the default pip index. |
| Artifact provenance/integrity | RED | Versions are locked but package hashes are not enforced; no repository-controlled offline wheelhouse is the canonical source. |
| Installer toolchain | AMBER | Inno Setup is a foreign build-time dependency. It is not required by the portable runtime but remains part of the installer path. |
| Source continuity | AMBER | GitVerse mirror exists, but it is currently populated by GitHub Actions rather than serving as a proven independent primary/recovery lane. |
| CI/release continuity | RED | Core automation still depends on GitHub-hosted runners/actions and live external package acquisition. |
| Windows platform APIs | ACCEPTED EXCEPTION | WinAPI, PowerShell, CIM and Windows are intrinsic to the Windows SKU and cannot be removed without ceasing to provide the Windows SKU. |
| Russian signing path | AMBER/GREEN FOUNDATION | Rutoken/CryptoPro architecture and contract tests exist, but CI smoke tests still execute on GitHub-hosted infrastructure with ephemeral Windows certificates. |

**Overall result: CONDITIONAL PASS.** The Windows product has a strong runtime sovereignty profile but **does not yet have a sovereign reproducible build/release chain**. No claim of a fully sovereign Windows build should be made until the P0 controls in section 10 are implemented and proven under an external-endpoint-denied build drill.

## 3. Current Windows dependency inventory

### 3.1 Runtime / product layer

| Component | Current role | Origin/control | Distribution | Criticality | Sovereignty classification | Mitigation / Russian-path decision |
|---|---|---|---|---|---|---|
| Arvectum application modules | Product logic, proxy lifecycle, recovery, diagnostics, GUI | ООО «Арвектум» | Source + bundled EXE | Critical | OWNED | Maintain IP provenance and release evidence. |
| CPython 3.12.10 | Interpreter bundled by PyInstaller | Python Software Foundation / international OSS | Bundled into EXE | Critical | FOREIGN OSS / VENDORABLE | Preserve approved CPython 3.12.10 x64 installer/embedded distribution, signatures and SHA256 in Arvectum-controlled storage. |
| Python standard library | Networking, subprocess, filesystem, JSON, threading, urllib, ctypes, etc. | PSF / Python contributors | Bundled with runtime | Critical | FOREIGN OSS / VENDORABLE | Same controlled Python toolchain snapshot. |
| Tcl/Tk / Tkinter | Desktop GUI | International OSS | Bundled with Python/PyInstaller | Critical for GUI | FOREIGN OSS / VENDORABLE | Archive the exact Tcl/Tk payload used by the approved Python build; keep license notice. |
| Windows / WinAPI | System proxy, registry, process and platform integration | Microsoft | OS-provided | Critical | PLATFORM EXCEPTION | Explicitly classify as Windows-SKU platform dependency; do not attempt replacement inside this SKU. |
| PowerShell | install/uninstall/recovery/build automation | Microsoft / OS-provided on supported Windows | OS/toolchain | High | PLATFORM EXCEPTION | Keep scripts compatible with Windows PowerShell where practical; do not introduce cloud PowerShell modules into runtime. |
| CIM / Windows management interfaces | Installer process handling and diagnostics | Microsoft / Windows | OS-provided | Medium | PLATFORM EXCEPTION | Keep use bounded to local Windows management. |
| User-configured upstream proxy | Business input for routed connectivity | Customer/user-selected | External network endpoint | Critical when proxy is enabled | CUSTOMER DEPENDENCY | Not a software supply-chain dependency. Product must remain provider-agnostic. |
| User-selected connection-test URL | Read-only connectivity probe | User/configuration | Network | Non-critical | CUSTOMER/TEST DEPENDENCY | Keep configurable; no mandatory Arvectum or foreign cloud endpoint should be required for runtime. |

### 3.2 Canonical Windows build dependencies

The repository pins Python `3.12.10`, pip `25.3`, and the following build packages:

| Component | Pinned version | Role | License / governance | Runtime dependency? | Sovereignty risk |
|---|---:|---|---|---|---|
| pip | 25.3 | Dependency installer/bootstrap | MIT | No | HIGH while used against public PyPI during build |
| PyInstaller | 6.22.0 | Freezes application into Windows EXE | GPL-2.0-or-later with bundling exception | Bootloader/runtime portions bundled | MEDIUM; source and wheels can be mirrored |
| altgraph | 0.17.5 | PyInstaller dependency graph support | MIT | Build-time | LOW after vendoring |
| packaging | 26.3 | Packaging metadata/version utilities | Apache-2.0 OR BSD-2-Clause | Build-time | LOW after vendoring |
| pefile | 2024.8.26 | PE parsing used by PyInstaller toolchain | MIT | Build-time | LOW after vendoring |
| pyinstaller-hooks-contrib | 2026.6 | PyInstaller hook collection | Apache/GPL components | Build-time | LOW/MEDIUM after vendoring and notice review |
| pywin32-ctypes | 0.2.3 | Windows ctypes helpers for PyInstaller | BSD-3-Clause | Build-time | LOW after vendoring |
| setuptools | 84.0.0 | Python build/package infrastructure | MIT | Build-time | LOW after vendoring |

These are predominantly **foreign open-source build dependencies**, not remote runtime services. Their nationality is therefore less important than Arvectum's ability to freeze, hash, audit and reproduce them from internal storage.

### 3.3 Installer dependency

`ArvectumProxyLauncherSetup.iss` uses **Inno Setup** for the installer edition. Inno Setup is not required for the portable ZIP/EXE path and is therefore separable from the core Windows product.

Sovereignty classification: **AMBER**.

Controls:

1. keep Windows portable as a first-class canonical release artifact;
2. retain a vetted Inno Setup installer/compiler distribution plus SHA256/signature evidence in controlled storage;
3. record the exact compiler version used for every installer release;
4. treat current commercial-license expectations as a procurement/compliance item;
5. do not make availability of the Inno Setup website or GitHub repository a release-time dependency;
6. if Inno Setup becomes unavailable/unacceptable, the portable release remains viable while an alternative installer path is selected.

No mature Russian-native drop-in installer compiler is asserted by this audit. The correct sovereignty measure is **dependency elimination at release time through vendoring and retention of the portable path**, rather than replacing a working installer tool merely because it is foreign.

## 4. Dependency acquisition audit

The canonical `tools/clean_build_windows.ps1` currently:

1. validates exact Python 3.12.10 x64;
2. creates an isolated `.build-venv`;
3. performs `pip install --upgrade "pip==25.3"`;
4. performs `pip install --no-deps -r requirements-build.lock.txt`;
5. runs `pip check` and records `pip freeze --all`;
6. compiles/tests the source;
7. builds a one-file Windows executable with PyInstaller;
8. hashes the EXE and ZIP with SHA256;
9. emits `build-result.json` with source commit, toolchain versions and artifact hashes.

This is a good reproducibility baseline, but it is **not sovereign dependency acquisition** because pip resolves/downloads packages from its configured/default external index at build time.

### Finding SO-WIN-001 — live public package-index dependency

**Severity: P0 / RED**

The canonical build requires live package acquisition unless the machine has a populated cache or alternate pip configuration. A public package index outage, regional restriction, dependency removal, DNS block, TLS problem or account/supply-chain compromise can break or alter the build path.

**Required control:** an Arvectum-controlled Windows wheelhouse/source cache containing every approved artifact needed for the exact toolchain.

### Finding SO-WIN-002 — version locks without enforced artifact hashes

**Severity: P0 / RED**

`requirements-build.lock.txt` fixes versions but does not identify exact wheel/sdist SHA256 digests, and the build does not use pip `--require-hashes`.

The repository does hash the final EXE/ZIP and lock file, which is valuable release evidence, but this protects the **output** rather than proving that every downloaded build input is the expected byte-for-byte artifact.

**Required control:** hash-lock every acquired package and build with `--no-index`, `--find-links <controlled-wheelhouse>`, and `--require-hashes` (or an equivalent verified internal acquisition mechanism).

### Finding SO-WIN-003 — Python base interpreter is locally discovered, not internally provisioned

**Severity: P0/P1 / AMBER**

The build requires exact Python 3.12.10 x64, but the canonical script searches the machine for an already-installed interpreter. This verifies version/architecture but not the installer/runtime provenance that produced it.

**Required control:** maintain an approved Python 3.12.10 Windows distribution with recorded upstream signature/hash and an internal provisioning procedure. The build evidence should include a trusted base-toolchain artifact identity, not only `sys.version`.

## 5. Runtime dependency audit

The Windows GUI entry point imports standard-library modules (`atexit`, `os`, `sys`, `subprocess`, `threading`, `tkinter`) and Arvectum-owned modules. Windows-specific fallbacks use `ctypes`/WinAPI. The built-in connectivity test uses standard-library `urllib` and sockets.

### Finding SO-WIN-004 — low third-party application-runtime surface

**Severity: positive control / GREEN**

There is no mandatory requests/Qt/Electron/.NET/cloud SDK or other third-party application framework in the Windows GUI entry point. This substantially reduces runtime lock-in and simplifies offline operation and source review.

The product runtime should preserve this principle unless a future dependency brings a clear benefit that outweighs sovereignty, licensing and packaging cost.

### Finding SO-WIN-005 — no mandatory SaaS runtime control plane

**Severity: positive control / GREEN**

The audited Windows product is a local proxy launcher, not a thin client for an Arvectum cloud service. User-configured upstream proxies and connectivity targets are external network resources, but they are product inputs rather than vendor-hosted application dependencies.

A future update service, telemetry platform, license server or account service would materially change this finding and must trigger a new sovereignty review.

## 6. Source-control and CI sovereignty

The repository has an automated GitVerse mirror, but the current mirror workflow runs on GitHub Actions, clones GitHub, and then pushes branches/tags to GitVerse.

### Finding SO-WIN-006 — GitVerse mirror is continuity storage, not yet an independent build lane

**Severity: P0 / RED-AMBER**

The mirror protects repository availability, but its freshness mechanism currently depends on GitHub. If GitHub is unavailable, blocked, or the GitHub App/workflows cannot run, the mirror cannot by itself prove that Arvectum can continue the full build/release process.

**Required controls:**

- configure GitVerse as an independently writable canonical/recovery remote;
- establish an independent GitVerse CI or Arvectum self-hosted Windows runner path;
- store the Windows dependency wheelhouse/toolchain outside GitHub-only artifacts;
- periodically build from the GitVerse checkout while GitHub and public PyPI are intentionally unavailable;
- compare source commit and final artifact hashes/release manifests with the canonical process.

GitHub may remain a high-priority development remote; the target is to remove **single-provider operational dependence**, not to prohibit its use.

## 7. Signing sovereignty boundary

The repository already contains Russian signing architecture work around Rutoken/CryptoPro and release-policy contracts. `windows-authenticode.yml` validates those contracts and performs a real Windows PE smoke test with an ephemeral CI certificate.

### Finding SO-WIN-007 — Russian production signing architecture exists, CI validation is still GitHub-hosted

**Severity: P1 / AMBER**

The production direction is compatible with a Russian trust/signing stack, but the automated smoke lane itself runs on GitHub-hosted runners. This is acceptable as a validation convenience but must not be the only proof path for a Russian production release.

**Required control:** keep production private keys/hardware tokens outside hosted CI, and prove signing/verifying on an owner-controlled Russian Windows workstation/runner using the approved Rutoken/CryptoPro path. Hosted CI should never become a requirement for access to the production signing key.

## 8. Licensing and third-party notices

Current `THIRD_PARTY_NOTICES.txt` covers Python, Tcl/Tk and PyInstaller and explicitly notes that the inspected one-file payload did not identify standalone OpenSSL/libffi binaries.

### Finding SO-WIN-008 — notices exist but are not a complete machine-derived final-payload inventory

**Severity: P1 / AMBER**

This is a good baseline, but sovereignty/IP hardening should derive the final notices and SBOM from the actual shipped artifact/toolchain rather than rely only on a hand-maintained notice file.

Required follow-up under APL-IP-001 / release hardening:

- generate SBOM for the final Windows payload;
- reconcile SBOM with `THIRD_PARTY_NOTICES.txt`;
- record component, version, source URL, license, artifact SHA256 and inclusion mode;
- retain license texts/evidence in the release provenance package;
- treat build-only dependencies separately from distributed runtime components.

## 9. Russian replacement / sovereignty decision matrix

| Foreign dependency | Replace with Russian component now? | Decision |
|---|---|---|
| Windows / WinAPI | No | Accepted platform boundary for the Windows SKU. Russian OS support is a separate Linux/Astra SKU, not a replacement inside this SKU. |
| CPython | No | Vendor/audit exact source/binary toolchain. Rewriting the runtime would increase risk without improving practical sovereignty. |
| Tcl/Tk | No | Vendor exact audited runtime; small, mature dependency. |
| PyInstaller stack | No immediate rewrite | Mirror/vend exact packages and source; retain ability to rebuild bootloader if required. |
| Public PyPI | **Yes, operationally** | Replace live dependency with Arvectum-controlled offline/internal wheelhouse + hashes. |
| GitHub as only source/CI | **Yes, operationally** | Add independent GitVerse + self-hosted/Russian CI recovery lane. GitHub may remain in normal operation. |
| Inno Setup live acquisition | **Yes, operationally** | Vendor approved compiler; keep portable release independent of installer compiler. |
| Foreign commercial code-signing CA | Avoid as production prerequisite | Russian Rutoken/CryptoPro path remains priority; international signing is optional/low-priority market expansion work. |

## 10. Remediation backlog

### P0 — required before “sovereign Windows build” claim

- [ ] **APL-IP-002-WIN-R1 — Offline Windows build inputs.** Create controlled wheelhouse/source archive for pip + all packages in `requirements-build.lock.txt`.
- [ ] **APL-IP-002-WIN-R2 — Hash-locked dependency installation.** Add exact SHA256 hashes and enforce offline `--no-index` / `--find-links` / `--require-hashes` build behavior.
- [ ] **APL-IP-002-WIN-R3 — Controlled CPython base toolchain.** Archive and verify the approved Python 3.12.10 x64 distribution and record its identity in build evidence.
- [ ] **APL-IP-002-WIN-R4 — Independent GitVerse Windows CI/recovery lane.** Build/test from GitVerse or an Arvectum-controlled checkout without GitHub being reachable.
- [ ] **APL-IP-002-WIN-R5 — External-endpoint-denied sovereignty drill.** Prove a clean Windows portable build with GitHub/PyPI blocked and only controlled/Russian/internal inputs available.

### P1 — release/IP hardening

- [ ] **APL-IP-002-WIN-R6 — Installer toolchain archive.** Freeze exact Inno Setup compiler distribution/source evidence and hashes; record compiler version in installer release manifest.
- [ ] **APL-IP-002-WIN-R7 — Payload-derived SBOM/notices reconciliation.** Generate SBOM from shipped artifact and reconcile licenses/notices.
- [ ] **APL-IP-002-WIN-R8 — Owner-controlled Russian signing proof.** Prove final production signing with Rutoken/CryptoPro outside hosted CI and preserve non-secret evidence.
- [ ] **APL-IP-002-WIN-R9 — Dual-remote recovery runbook.** Document authoritative recovery procedure if GitHub is unavailable or account access is lost.

### P2 — resilience / long-term independence

- [ ] Maintain Windows portable ZIP as a release format independent of installer technology.
- [ ] Retain source archives for critical foreign OSS build tools, not only prebuilt wheels.
- [ ] Periodically test rebuilding the PyInstaller bootloader/toolchain on a controlled Windows image.
- [ ] Add sovereignty review gate when introducing telemetry, auto-update, cloud licensing, mandatory account services or new runtime libraries.

## 11. Acceptance criteria for APL-IP-002-WIN-R5

The Windows sovereignty drill is PASS only when all conditions hold:

1. source checkout is available from GitVerse/controlled Arvectum storage without GitHub access;
2. Python base toolchain is installed/provisioned from a controlled verified artifact;
3. all Python build dependencies are resolved from the controlled wheelhouse with exact hashes;
4. public PyPI and GitHub are blocked for the build environment;
5. tests and canonical PyInstaller portable build pass;
6. final EXE and ZIP SHA256 values are produced;
7. build manifest records source commit, Python/toolchain versions and controlled input-set identity;
8. the resulting portable package runs on a clean supported Windows machine without Python or package-index access;
9. production signing, when required, is executed through the approved owner-controlled Rutoken/CryptoPro path rather than a hosted-CI private key;
10. SBOM and third-party notices are preserved with release evidence.

## 12. Audit evidence from repository

- `BUILD_PYTHON_VERSION` — exact Python `3.12.10`.
- `requirements-build.lock.txt` — exact build package versions.
- `tools/clean_build_windows.ps1` — canonical isolated build, online pip acquisition, tests, PyInstaller, SHA256 and build manifest.
- `build_exe.bat` — delegates Windows build to the canonical PowerShell script.
- `proxy_gui.py` — Windows GUI standard-library/internal-module imports and WinAPI fallback.
- `connection_test.py` — standard-library connectivity tests with configurable target URL.
- `THIRD_PARTY_NOTICES.txt` — current distributed third-party notices.
- `ArvectumProxyLauncherSetup.iss` — Inno Setup installer path and local PowerShell/CIM integration.
- `.github/workflows/mirror-to-gitverse.yml` — GitHub-triggered GitVerse mirror.
- `.github/workflows/windows-authenticode.yml` — Authenticode/Russian-signing contract and Windows smoke validation.

## 13. External verification references

Verified on 2026-08-16 against the publishers' current documentation/registries:

- Python licensing: https://docs.python.org/3/license.html
- PyInstaller package/license: https://pypi.org/project/pyinstaller/6.22.0/ and https://pyinstaller.org/en/stable/license.html
- packaging 26.3: https://pypi.org/project/packaging/26.3/
- setuptools 84.0.0: https://pypi.org/project/setuptools/84.0.0/
- pip 25.3: https://pypi.org/project/pip/25.3/
- Inno Setup current downloads/licensing: https://jrsoftware.org/isdl.php and https://jrsoftware.org/isorder.php
- GitVerse documentation: https://docs.gitverse.ru/

## 14. Final decision

**APL-IP-002-WIN is complete.**

The current Windows architecture is favorable for sovereignty because the shipped application has a small and mostly self-contained runtime surface. The principal exposure lies outside the application code: **public PyPI at clean-build time, GitHub-hosted CI/source continuity, unmanaged provenance of the base Python installation, and the foreign installer toolchain**.

The correct next move is not to rewrite Python/PyInstaller in-house. It is to make the existing open-source stack **Arvectum-controlled at the artifact, hash, source-mirror and CI levels**. Completing P0 remediation converts the Windows build from “reproducible when foreign infrastructure is available” to “reproducible from controlled/Russian/internal infrastructure.”
