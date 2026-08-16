# APL-REL-011 — Russian signed-release integration / ОТУЦ readiness

**Status:** IMPLEMENTED / REPOSITORY READINESS COMPLETE / OWNER-OPERATED RELEASE SIGNING REQUIRED PER RELEASE  
**Decision date:** 2026-08-16  
**Primary market:** Russian Federation  
**Owner:** ООО «Арвектум»

## 1. Result of APL-REL-010 carried forward

APL-REL-010 closed successfully on the owner-operated Windows host `ARUTYUNOVNS` using CryptoPro CSP `5.0.18138.0` and the existing Rutoken-backed ООО «Арвектум» certificate.

Approved certificate identity:

```text
Thumbprint: EE1CFA955BA22F03C39C76B183D94CD37494582E
Issuer: Федеральная налоговая служба
Detached CryptoPro signing: PASS
Detached CryptoPro verification: PASS
Code Signing EKU 1.3.6.1.5.5.7.3.3: ABSENT
Classification: RELEASE-EVIDENCE-ONLY
Production embedded code signing: NOT ACTIVATED
```

This task therefore integrates the qualified detached release-evidence path into the real release process and keeps embedded executable signing behind a separate ОТУЦ readiness gate.

## 2. Canonical Russian release baseline

Until a production-ready domestic code-signing identity is issued and separately proven, the Russian release baseline is:

```text
approved main commit
  -> immutable version tag
  -> green exact-SHA CI/evidence
  -> final Windows release assets
  -> transfer final assets to owner-operated Windows signing station
  -> generate SHA256SUMS.txt over final downloadable assets
  -> sign SHA256SUMS.txt with Rutoken/CryptoPro УКЭП
  -> verify detached signature with CryptoPro
  -> export public signer certificate
  -> generate signing-evidence.json
  -> publish assets + four evidence files
```

Canonical evidence files:

```text
SHA256SUMS.txt
SHA256SUMS.txt.sig
signer-certificate.cer
signing-evidence.json
```

The qualified signature identifies ООО «Арвектум» and binds the final artifact hashes. It is not represented as Microsoft SmartScreen reputation or stock-Windows publisher trust.

## 3. Implemented production integration

Canonical owner-operated script:

```text
tools/russian_signed_release.ps1
```

Example invocation on the controlled Windows signing station:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\russian_signed_release.ps1 `
  -ReleaseDirectory "C:\release\Arvectum-Proxy-Launcher-1.0.0" `
  -Version "1.0.0" `
  -GitTag "v1.0.0" `
  -GitCommit "<40-character-main-commit>" `
  -CertificateThumbprint "EE1CFA955BA22F03C39C76B183D94CD37494582E"
```

The script:

- requires explicit release directory, version, tag, exact 40-character commit and signer thumbprint;
- fails on version/tag mismatch;
- hashes every final file in the release directory except reserved evidence files;
- generates deterministic filename-sorted `SHA256SUMS.txt` using SHA-256;
- verifies every manifest entry before signing;
- requires an accessible private key in the Windows certificate store but never exports it;
- signs the manifest through CryptoPro `csptest -sfsign` using a detached CMS/PKCS#7 signature;
- verifies the signature through CryptoPro and fails closed without a positive verification marker;
- exports only the public certificate;
- re-hashes every release asset after signing to detect any byte change during the ceremony;
- writes machine-readable `signing-evidence.json` with release identity, certificate metadata and asset hashes;
- never accepts a PIN parameter and never stores a PIN;
- never accepts PFX/P12 key material;
- never activates embedded PE signing.

## 4. Evidence contract

`signing-evidence.json` records at minimum:

- schema version and task ID;
- product and release version;
- Git tag and exact commit;
- signing mode `russian-qualified-evidence`;
- signing host and CryptoPro version;
- signer subject, issuer, thumbprint, serial and expiry;
- private-key availability without private-key export;
- Code Signing EKU assessment;
- current certificate classification;
- explicit `embedded_code_signing_activated: false`;
- explicit `otuc_production_certificate_used: false`;
- manifest and signature hashes;
- detached verification result;
- final asset names, sizes and SHA-256 values.

Forbidden evidence content:

- token PIN;
- passwords;
- private key material;
- PFX/P12 exports;
- secret environment variables;
- unattended signing credentials.

## 5. CI boundary

GitHub/GitVerse CI is allowed to test the **repository contract** only.

The workflow:

```text
.github/workflows/russian-signed-release-readiness.yml
```

checks that:

- the signing script, task document and tests are present;
- the script remains SHA-256 + detached-signature based;
- no embedded code signing is enabled;
- no GitHub secret, Rutoken, CryptoPro invocation or certificate credential is placed into the CI workflow.

CI does **not** access the production Rutoken and does **not** create production signatures.

## 6. ОТУЦ readiness status as of 2026-08-16

Current public first-party material from CryptoPro states that the Отраслевой технологический удостоверяющий центр (ОТУЦ) has been operating in test mode since November 2025. CryptoPro, InfoTeCS and Security Code publicly reported a successful software-signing experiment using certificates issued through the ОТУЦ system while it was in test operation.

Therefore Arvectum classifies ОТУЦ as:

```text
TECHNICALLY RELEVANT: YES
DOMESTIC STRATEGIC TARGET: YES
PUBLIC TEST/PILOT EVIDENCE: YES
GENERAL PRODUCTION ENROLLMENT FOR ARVECTUM PROVEN: NO
ARVECTUM CERTIFICATE ISSUED: NO
ARVECTUM EMBEDDED SIGNING POC: NO
PRODUCTION EMBEDDED SIGNING ACTIVATED: NO
```

APL-REL-011 must not invent an enrollment URL, certificate price, SLA, public issuance procedure, timestamp endpoint or stock-Windows trust result until each is confirmed from the responsible ОТУЦ/АНО НТЦ ЦК/operator channel.

## 7. ОТУЦ acceptance checklist

Before any ОТУЦ certificate can become a production dependency, all items below must be closed with real evidence.

### Enrollment and legal identity

- [ ] Confirm that ООО «Арвектум» is eligible to enroll.
- [ ] Obtain the current official application/onboarding procedure directly from the operator.
- [ ] Confirm required organization documents and authorized representative process.
- [ ] Confirm certificate issuance, renewal, revocation and incident-response rules.
- [ ] Confirm commercial terms or explicitly documented pilot terms.

### Certificate profile

- [ ] Obtain a real Arvectum certificate or controlled test certificate.
- [ ] Confirm Code Signing EKU / intended application policy.
- [ ] Confirm supported GOST algorithms and CryptoPro provider path.
- [ ] Confirm private-key storage requirements and whether Rutoken/current hardware can be used.
- [ ] Confirm the issuing hierarchy and complete trust chain.

### Signing mechanics

- [ ] Sign the actual portable application EXE.
- [ ] Verify the embedded signature using the prescribed domestic verification stack.
- [ ] Build the installer from the already-signed application binary.
- [ ] Sign the installer EXE.
- [ ] Verify the installer signature.
- [ ] Confirm timestamp mechanism, endpoint, accepted profile and post-expiry verification behavior.

### Target-platform trust

- [ ] Test Windows 10/11 behavior with the documented domestic trust configuration.
- [ ] Test Astra Linux.
- [ ] Test ALT Linux.
- [ ] Test RED OS.
- [ ] Record whether trust is native, package-installed, CryptoPro-provided or application-specific.
- [ ] Never label a platform `trusted` based only on cryptographic signature validity.

### Release integration

- [ ] Add a separate embedded-signing mode only after the real POC passes.
- [ ] Keep sign -> verify -> package -> sign installer -> verify -> checksum ordering.
- [ ] Regenerate final SHA256SUMS.txt after the last byte-changing embedded signature.
- [ ] Qualified-sign the final manifest with the company release-evidence key.
- [ ] Preserve fail-closed publication gates.

## 8. Fail-closed rules for the current baseline

The release must not be published as a Russian signed release when any of these conditions is true:

- final artifact directory is empty;
- version and Git tag disagree;
- Git commit is not recorded as a full SHA;
- certificate cannot be resolved by the explicitly approved thumbprint;
- certificate private key is unavailable;
- any release asset changes after manifest generation;
- detached signature is missing;
- CryptoPro verification is not positive;
- signer certificate export fails;
- evidence JSON is absent;
- evidence claims embedded code signing when the ОТУЦ POC has not passed.

## 9. Publication semantics

A release signed under the current baseline may be described as:

```text
Release integrity protected by SHA-256.
Release manifest signed by qualified electronic signature of ООО «Арвектум» using CryptoPro/Rutoken.
Public signer certificate and machine-readable signing evidence included.
```

It must not be described as:

```text
Microsoft-trusted Authenticode signed
SmartScreen trusted
ОТУЦ code-signed
Windows publisher trusted
```

unless those properties are separately proven for that exact release.

## 10. Acceptance criteria

- [x] REL-010 hardware evidence is carried forward without changing its classification.
- [x] Existing ООО «Арвектум» УКЭП is integrated into the final release-manifest signing flow.
- [x] Canonical owner-operated production script is implemented.
- [x] Every final release asset is covered by SHA-256 before detached signing.
- [x] Assets are reverified after signing.
- [x] Detached CryptoPro verification is mandatory and fail-closed.
- [x] Public certificate export and non-secret signing evidence are generated.
- [x] PIN/PFX/private-key CI storage is prohibited by design and tests.
- [x] Embedded code signing remains disabled.
- [x] ОТУЦ is treated as the primary domestic code-signing target but not falsely treated as generally production-available to Arvectum.
- [x] Concrete ОТУЦ enrollment/profile/timestamp/platform acceptance checklist is defined.
- [x] CI readiness tests do not touch the production signing key.

## 11. Closure classification

```text
APL-REL-011 repository integration: PASS
Russian qualified signed-release path: READY
Current Rutoken УКЭП classification: RELEASE-EVIDENCE-ONLY
Owner-operated signing required for each release: YES
ОТУЦ technical readiness checklist: READY
ОТУЦ production enrollment for ООО «Арвектум»: NOT YET PROVEN
Embedded Russian code signing: NOT ACTIVATED
Foreign code-signing dependency: NO
```

## 12. Next task

**APL-REL-012 — Russian release verification & end-user trust UX**

Implement and document the consumer-side verification path for `SHA256SUMS.txt` + detached CryptoPro signature + public signer certificate, including a simple Russian-language verification instruction/tooling path and explicit distinction between qualified release authenticity, cryptographic integrity and OS-native publisher trust.
