# APL-REL-009 — Russian production signing architecture

**Status:** ARCHITECTURE APPROVED / PRODUCTION SIGNING NOT YET ACTIVE  
**Decision date:** 2026-08-16  
**Primary market:** Russian Federation  
**Owner:** ООО «Арвектум»

## 1. Decision

Arvectum Proxy Launcher adopts a **Russia-first production signing architecture**.

The production trust path is not based on a foreign commercial code-signing CA. The current Windows Authenticode foundation from APL-REL-008 is retained as a transport/verification mechanism, but provider selection is governed by this document.

Priority order:

1. **Russian qualified release evidence using the existing ООО «Арвектум» УКЭП on a non-exportable hardware token through CryptoPro.**
2. **Russian code-signing identity / Отраслевой технологический удостоверяющий центр (ОТУЦ)** once production availability, certificate profile, timestamping, verification and target-OS trust behavior are verified.
3. **Foreign code-signing providers** only as a future international-market compatibility track. They are not a dependency for the Russian production release.

No GlobalSign, DigiCert, Sectigo, Microsoft Trusted Signing or similar foreign provider is required for the Russian production baseline.

## 2. Why the existing УКЭП is not treated as an automatic Authenticode certificate

The company already has a Rutoken-backed qualified electronic signature and CryptoPro infrastructure. This is suitable for producing legally meaningful Russian electronic signatures over release evidence, but it must not be assumed to be a Windows code-signing certificate.

Before any certificate may be used for embedded PE/Authenticode signing, APL-REL-010 must prove all of the following:

- the certificate profile explicitly permits code signing;
- the Code Signing EKU (`1.3.6.1.5.5.7.3.3`) is present when required by the selected implementation;
- the private key remains non-exportable;
- CryptoPro/provider integration can sign the actual application and installer;
- timestamping is supported by an accepted Russian service;
- verification behavior is known on each supported target OS;
- using the certificate this way is consistent with the issuing CA policy and applicable Russian rules.

Until that proof exists, the current УКЭП is used for **detached release evidence**, not silently repurposed as an Authenticode identity.

## 3. Trust model

The release is protected by three independent layers.

### Layer A — reproducible release provenance

Generated automatically before owner signing:

- immutable Git tag pointing to `main`;
- green CI for the tagged commit;
- canonical Windows build;
- SBOM and release evidence;
- final artifact inventory;
- SHA-256 checksums.

This layer proves what source/build produced the candidate artifacts but does not by itself prove the legal identity of ООО «Арвектум».

### Layer B — Russian qualified release signature

The final release checksum manifest is signed by the owner-operated Russian signing station using the ООО «Арвектум» qualified electronic signature stored on Rutoken.

Canonical evidence set:

```text
SHA256SUMS.txt
SHA256SUMS.txt.sig
signer-certificate.cer
signing-evidence.json
```

`SHA256SUMS.txt.sig` is a detached electronic signature produced through the approved CryptoPro/Rutoken stack. The exact CMS/CAdES profile and command are selected and proven in APL-REL-010 rather than guessed in this architecture task.

The signed manifest covers every final downloadable release asset. If an executable is modified by later embedded code signing, the checksums and qualified signature must be regenerated afterwards.

### Layer C — Russian OS-integrated code signature

When a production Russian code-signing certificate becomes available and passes APL-REL-010:

1. sign the portable application EXE;
2. verify it;
3. build the installer from that signed application binary;
4. sign the installer EXE;
5. verify it;
6. generate final SHA-256 checksums;
7. sign the checksum manifest with the qualified company signature;
8. publish only after all gates pass.

The intended provider class is the Russian code-signing infrastructure represented by ОТУЦ or a successor domestic mechanism with equivalent trust goals.

## 4. Windows trust boundary

A Russian signature and a Microsoft-trusted signature are not the same trust domain.

Stock Windows does not automatically gain trust in an arbitrary Russian root or GOST signature merely because the signature is legally valid in Russia. CryptoPro publicly identified the absence of Russian roots in foreign operating systems as the core technical problem and described ОТУЦ as the domestic response.

Therefore:

- **legal validity / Russian qualified signature** is one property;
- **cryptographic integrity** is another property;
- **Windows built-in publisher trust / SmartScreen reputation** is a third property.

APL must not report one as proof of another.

For the Russian market, the release must remain verifiable through the published Russian signature and checksums even where stock Windows does not display a fully trusted publisher chain.

## 5. Signing station / NUC architecture

Production private keys are never stored in GitHub, GitVerse, repository secrets, PFX/P12 files or cloud CI runners.

Target owner-operated station:

```text
Dedicated Windows NUC / signing workstation
  ├─ current supported Windows
  ├─ CryptoPro CSP
  ├─ Rutoken drivers/middleware as required
  ├─ Windows SDK SignTool only where the selected code-signing path requires it
  ├─ release-signing scripts from this repository
  └─ physically attached Rutoken
```

Rules:

- private key must remain non-exportable;
- token PIN must never be committed or stored in GitHub secrets;
- signing requiring the director's qualified signature is owner-operated;
- no unattended remote service may use the Rutoken without an explicitly approved future key-custody design;
- the station must verify the release candidate against the expected Git commit/tag before signing;
- signing logs may record certificate metadata and artifact hashes, but never PINs or secret key material.

A future self-hosted runner may orchestrate non-secret steps, but the production private-key boundary remains local to the controlled signing station.

## 6. Canonical release flow

### Current Russian baseline — qualified evidence, no production code-signing certificate yet

```text
main + green CI
  -> immutable version tag
  -> canonical Windows build
  -> portable ZIP + installer EXE
  -> final SHA256SUMS.txt
  -> transfer candidate + provenance to signing station
  -> owner verifies tag/commit/hashes
  -> Rutoken/CryptoPro signs SHA256SUMS.txt
  -> signature verification
  -> publish artifacts + SHA256SUMS.txt + .sig + signer certificate + evidence
```

### Future OТУЦ-enabled baseline

```text
main + green CI
  -> immutable version tag
  -> canonical application build
  -> transfer unsigned PE candidate to signing station
  -> Russian code-sign portable application EXE
  -> verify embedded signature
  -> build installer using signed application EXE
  -> Russian code-sign installer EXE
  -> verify embedded signature
  -> generate final packages and SHA256SUMS.txt
  -> Rutoken/CryptoPro qualified-sign SHA256SUMS.txt
  -> verify detached qualified signature
  -> publish only if every gate passes
```

## 7. Fail-closed release gates

A Russian production release must fail closed when any required condition is false.

Required baseline gates:

- tag/version mismatch;
- tagged commit is not approved `main` ancestry;
- canonical build or release tests fail;
- artifact list differs from the manifest;
- SHA-256 verification fails;
- qualified signature over `SHA256SUMS.txt` is absent or invalid once Russian production signing is activated;
- signer certificate identity does not match the approved ООО «Арвектум» signing identity;
- signing evidence refers to a different commit, version or artifact set.

Additional gates once embedded Russian code signing is activated:

- portable EXE is unsigned or verification fails;
- installer EXE is unsigned or verification fails;
- publisher identity mismatch;
- required timestamp is absent/invalid;
- final checksums were generated before the last byte-changing signing operation.

## 8. Signing evidence record

Each signed release must produce a machine-readable `signing-evidence.json` containing non-secret metadata at minimum:

```json
{
  "product": "Arvectum Proxy Launcher",
  "version": "X.Y.Z",
  "git_tag": "vX.Y.Z",
  "git_commit": "<40-hex-sha>",
  "signing_mode": "russian-qualified-evidence|russian-code-signing",
  "manifest": "SHA256SUMS.txt",
  "manifest_signature": "SHA256SUMS.txt.sig",
  "signer_subject": "<certificate subject>",
  "signer_thumbprint": "<certificate thumbprint>",
  "certificate_serial": "<serial>",
  "certificate_not_after": "<ISO-8601>",
  "signature_verified": true,
  "embedded_code_signing_verified": false
}
```

No PIN, password, private-key path or private-key material may appear in this record.

## 9. Provider policy

### Primary — Russian

- CryptoPro / approved Russian cryptographic stack for qualified release evidence.
- Rutoken or equivalent certified non-exportable hardware key carrier.
- ОТУЦ or successor domestic code-signing infrastructure once production-ready and verified.
- Russian OS trust integration is evaluated explicitly for Astra Linux, ALT Linux and RED OS as those release tracks become active.

### Deferred — international compatibility

Foreign CA / Microsoft-rooted Authenticode may be reconsidered only when Arvectum has a justified international distribution requirement. It is not part of the current release blocker, not part of the Russian trust root, and must not displace the domestic signing evidence path.

## 10. Relationship to APL-REL-008

APL-REL-008 remains valid as an Authenticode engineering foundation:

- certificate-store based signing;
- no PFX/password repository contract;
- fail-closed verification;
- SHA-256 digest;
- production timestamp requirement;
- correct byte-ordering of sign -> checksum -> publish.

APL-REL-009 supersedes only the **provider/production trust strategy**. Production activation remains off until the Russian POC is completed.

## 11. Verified external basis as of 2026-08-16

Architecture decisions were checked against current primary/first-party material:

- CryptoPro, 2026-06-22: announcement of the Отраслевой технологический удостоверяющий центр for code-signing certificates; states that the service has operated in test mode since November 2025 and identifies the absence of Russian roots in foreign OS trust stores as the core problem.
- FNS Russia: current guidance on qualified electronic signatures, non-exportable protected key carriers and verification against accredited CA trust chains.
- CryptoPro documentation: support for Authenticode-related signing/timestamp technology and Russian cryptographic providers.

This architecture intentionally does **not** claim that ОТУЦ is generally available to Arvectum in production today. Availability, enrollment, certificate profile, algorithms, timestamping and OS trust behavior are acceptance items for APL-REL-010.

## 12. Acceptance criteria

- [x] Russia-first signing strategy is the canonical production policy.
- [x] Existing Rutoken/УКЭП is assigned a valid role without falsely treating it as an automatic code-signing certificate.
- [x] ОТУЦ is selected as the preferred domestic code-signing direction, gated by a real POC.
- [x] Foreign code-signing providers are explicitly deferred to international compatibility work.
- [x] Private-key custody is restricted to an owner-operated hardware-backed signing station.
- [x] CI/cloud runners never require an exportable production signing key.
- [x] Canonical ordering of embedded signing, checksums, qualified manifest signing and publication is defined.
- [x] Fail-closed release gates are defined.
- [x] Machine-readable non-secret signing evidence contract is defined.
- [x] Production signing remains disabled until APL-REL-010 proves the real Rutoken/CryptoPro path.

## 13. Next task

**APL-REL-010 — Rutoken/CryptoPro signing POC**

Prove the real certificate/token/provider behavior on the Windows owner-operated machine, inventory the current ООО «Арвектум» certificate profile, perform a real detached-signature round trip over a disposable release manifest, and determine whether any available certificate can validly participate in code signing without changing the approved key-custody boundary.
