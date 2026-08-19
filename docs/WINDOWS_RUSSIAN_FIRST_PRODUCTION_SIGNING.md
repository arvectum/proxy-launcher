# [Win] Russian-first production signing

Status: **repository implementation complete; owner-operated physical signing ceremony pending**.

Date: 2026-08-19  
Product version: `0.2.3`

## 1. Purpose

This gate turns the already-built Windows 0.2.3 artifacts into one governed Russian-first production release without changing or rebuilding their bytes.

The canonical entry point is:

```powershell
.\tools\windows_russian_production_signing.ps1
```

It composes the existing APL-REL-011, APL-REL-012 and APL-REL-013 primitives into one fail-closed owner-operated ceremony.

## 2. Sealed production inputs

The ceremony accepts only the artifacts recorded in `docs/evidence/WINDOWS_INNO_6_7_1_PRODUCTION_BUILD_EVIDENCE.json`:

| Artifact | Required identity |
|---|---|
| Portable ZIP | `Arvectum-Proxy-Launcher-0.2.3-windows-x64-portable.zip` |
| Portable ZIP SHA256 | `62d313547b4d8c2c8e6951d6cd866bb954fdf199ad7650063c8ed3bfbc455801` |
| Portable EXE SHA256 recorded in provenance | `f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a` |
| Installer | `Arvectum-Proxy-Launcher-0.2.3-windows-x64-setup.exe` |
| Installer SHA256 | `5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414` |
| Installer size | `17559854` bytes |
| Artifact build commit | `54ce2585222948b51c67510ea620516ea6c3f876` |

Any filename, hash or installer-size mismatch is a hard failure.

## 3. Dual-commit provenance

The final package deliberately records two different Git identities:

- `artifact_build_commit` — the commit from which the sealed portable and installer artifacts were built;
- `release_policy_commit` — the later canonical `main` commit containing the release/signing governance used for the ceremony.

This is not rewritten as a fictitious single provenance point. The ceremony verifies that the artifact build commit is an ancestor of the release-policy commit and that every intervening change is release-only. Any runtime/product/build-input drift forces a rebuild before signing.

The signed package contains `WINDOWS_BUILD_PROVENANCE.json` with both identities.

## 4. Trust model

The current Russian-first production contour is:

1. SHA-256 hashes over the exact final customer release files;
2. detached CryptoPro signature over `SHA256SUMS.txt` using the governed ООО «Арвектум» Rutoken certificate;
3. exported public signer certificate;
4. bundled end-user verifier;
5. mandatory positive verification;
6. mandatory negative tamper test;
7. exact clean/tagged/canonical Git provenance;
8. final fail-closed `PUBLISH` decision.

The currently governed certificate remains classified as `RELEASE-EVIDENCE-ONLY`. The ceremony **does not claim** embedded PE Authenticode signing, Microsoft SmartScreen reputation, or native Windows publisher trust.

Embedded code signing remains a separate future gate for a separately approved domestic code-signing certificate and proven toolchain.

## 5. Security boundary

The ceremony must run on the owner-operated Windows signing station with the physical Rutoken available.

The script:

- has no PIN/password/PFX parameters;
- never exports a private key;
- never stores the token PIN;
- allows CryptoPro/the token middleware to request the PIN interactively;
- refuses to run outside Windows;
- refuses a dirty worktree;
- refuses a branch other than canonical `main`;
- requires the release tag to resolve to the exact current `HEAD`;
- requires the output release directory to be outside the Git worktree and empty;
- verifies that the governed certificate is present, currently valid, identifies АРВЕКТУМ and exposes the Rutoken-backed private key;
- rejects any operator attempt to substitute another signing certificate.

## 6. Canonical ceremony

Before running the ceremony, the final release-policy changes must be merged to `main`, the local checkout must be updated and clean, and the exact release tag must point to that `main` commit.

Example:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\windows_russian_production_signing.ps1 `
  -PortableZipPath 'C:\Arvectum\Artifacts\0.2.3\Arvectum-Proxy-Launcher-0.2.3-windows-x64-portable.zip' `
  -InstallerPath 'C:\Arvectum\Artifacts\0.2.3\Arvectum-Proxy-Launcher-0.2.3-windows-x64-setup.exe' `
  -ReleaseDirectory 'C:\Arvectum\Releases\0.2.3-russian-production' `
  -GitTag 'v0.2.3'
```

The governed production release identity is pinned in the repository to certificate thumbprint:

`EE1CFA955BA22F03C39C76B183D94CD37494582E`

If the release identity is intentionally rotated later, the pinned thumbprint, tests, release governance and evidence expectations must be changed together through repository review. An operator-supplied different thumbprint is rejected by the production ceremony.

## 7. Final customer release set

Before signing, the orchestrator stages at least:

- the exact portable ZIP;
- the exact Inno Setup installer;
- `THIRD_PARTY_NOTICES.txt`;
- `LICENSE.txt`;
- `WINDOWS_INNO_6_7_1_PRODUCTION_BUILD_EVIDENCE.json`;
- `WINDOWS_BUILD_PROVENANCE.json`;
- `README_RUSSIAN_RELEASE.txt`;
- `verify_russian_release.ps1`;
- `VERIFY_RUSSIAN_RELEASE.cmd`.

APL-REL-011 then adds:

- `SHA256SUMS.txt`;
- `SHA256SUMS.txt.sig`;
- `signer-certificate.cer`;
- `signing-evidence.json`.

APL-REL-013 writes its publication decision **outside** the signed directory so it cannot invalidate the signed customer set.

## 8. Publication rule

A Windows release is publishable only when the orchestration ends with:

```text
Windows Russian-first production signing ceremony: PASS
Publication decision: ...production-release-gate.json
Qualified detached release evidence: PRESENT AND VERIFIED
Embedded Authenticode/SmartScreen trust claimed: NO
```

The decision JSON must contain `decision = PUBLISH`.

Any missing artifact, hash mismatch, product drift, tag mismatch, dirty checkout, wrong/expired/substituted signer, failed detached verification, changed release asset, missing verifier, failed positive verification, or unexpectedly successful tamper test means **DO NOT PUBLISH**.

## 9. Completion boundary

Repository-side implementation is complete when the orchestration script, contract tests, CI syntax gate and this runbook are merged to canonical `main`.

The production-signing task itself is complete only after the owner-operated ceremony is executed against the sealed 0.2.3 binaries and the resulting signed release directory plus `.production-release-gate.json` are retained as release evidence.
