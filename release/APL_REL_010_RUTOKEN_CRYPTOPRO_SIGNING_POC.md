# APL-REL-010 — Rutoken/CryptoPro signing POC

**Status:** IMPLEMENTED / OWNER-OPERATED HARDWARE RUN REQUIRED  
**Decision date:** 2026-08-16  
**Primary POC host:** Windows owner-operated notebook  
**Secondary host:** MacBook, compatibility-only follow-up  
**Owner:** ООО «Арвектум»

## 1. Decision: use Windows as the primary POC host

The primary APL-REL-010 run is performed on the Windows notebook where CryptoPro CSP, the company certificate(s), and the Rutoken are already configured.

Reasons:

1. The immediate release target is Windows (`.exe` portable application and installer), so the POC must observe the same Windows certificate store, provider integration and trust behavior used by the release toolchain.
2. The repository already uses Windows SignTool/Authenticode for its provider-neutral engineering foundation.
3. The POC needs to inspect whether the current certificate profile contains the Code Signing EKU (`1.3.6.1.5.5.7.3.3`). This is directly actionable on the same Windows host where a future embedded-signing probe would run.
4. Rutoken/CryptoPro interaction can remain owner-operated and hardware-backed without exporting the private key.
5. A successful Windows POC answers the release-blocking question. Repeating detached signing on macOS may later prove portability, but it is not required to close the Windows release blocker.

The MacBook remains useful as a second-stage interoperability check for CryptoPro/Rutoken and detached signatures. It is intentionally not the first POC host.

## 2. What this POC proves

APL-REL-010 is split into two separate questions and does not conflate them.

### A. Qualified detached release evidence

Prove that the existing ООО «Арвектум» certificate/private key on Rutoken can, through the installed CryptoPro CSP stack:

- be discovered from the Windows certificate store;
- keep the private key non-exported;
- sign a disposable `SHA256SUMS.txt` manifest;
- create a detached CMS/PKCS#7 signature;
- verify that signature successfully using CryptoPro;
- export only the public signer certificate;
- produce machine-readable non-secret evidence.

A PASS here is sufficient to validate the Layer B release-evidence path from APL-REL-009.

### B. Embedded code-signing eligibility

Inspect the selected certificate profile and determine whether it is even a candidate for embedded Windows code signing.

The POC checks for the Code Signing EKU:

```text
1.3.6.1.5.5.7.3.3
```

Interpretation:

- **EKU absent:** the current certificate is not treated as a code-signing certificate. No embedded signing attempt is made with it.
- **EKU present:** the certificate is only a *candidate profile*. This still does not prove that the issuing CA policy permits software signing, that a suitable Russian timestamp path exists, or that target Windows/Russian OS trust behavior is acceptable.

Therefore APL-REL-010 never turns a normal УКЭП into a production Authenticode identity by assumption.

## 3. Implemented POC runner

Canonical script:

```text
tools/rutoken_cryptopro_poc.ps1
```

The script has two modes.

### Inspect mode — no signing

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\rutoken_cryptopro_poc.ps1 -Mode Inspect
```

This:

- locates `csptest.exe` from CryptoPro CSP;
- prints the CryptoPro file version;
- inventories certificates from `Cert:\CurrentUser\My`;
- shows whether each certificate has an accessible private key;
- shows whether the Code Signing EKU is present.

No PIN is requested and no signing occurs.

### Run mode — real disposable signing round trip

Use the thumbprint of the company signing certificate selected from Inspect mode:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\rutoken_cryptopro_poc.ps1 `
  -Mode Run `
  -CertificateThumbprint "<THUMBPRINT>"
```

An explicit thumbprint is the governed path and avoids ambiguity when several certificates are installed. The script falls back to automatic selection only when the selected certificate store contains exactly one certificate with an accessible private key.

The script must **not** be passed a PIN. CryptoPro/Rutoken may prompt the owner interactively when the private key is used.

## 4. POC artifacts

Default output directory:

```text
%TEMP%\Arvectum\APL-REL-010\
```

Generated files:

```text
poc-artifact.txt
SHA256SUMS.txt
SHA256SUMS.txt.sig
signer-certificate.cer
signing-evidence.json
```

`signing-evidence.json` records only non-secret information including:

- host and OS;
- CryptoPro executable path/version;
- certificate subject, issuer, serial, validity and thumbprint;
- private-key availability flag;
- provider name when Windows exposes it;
- EKU OIDs/names;
- Code Signing EKU assessment;
- manifest/signature SHA-256 hashes;
- detached verification result;
- explicit flags that private-key export, PIN storage, Authenticode activation and production signing did not occur.

## 5. Safety boundary

The POC must preserve all APL-REL-009 key-custody rules.

Mandatory rules:

- no PFX/P12 export;
- no private-key export;
- no token PIN in the repository, shell history, environment variables, CI secrets or evidence JSON;
- no GitHub-hosted runner access to the production token;
- no unattended token use;
- public certificate export is allowed;
- POC output must not be committed unless explicitly reviewed for non-secret content;
- a successful detached-signature POC does **not** activate production signing automatically.

## 6. Why `csptest` is the POC primitive

The POC uses the `csptest -sfsign` path supplied with CryptoPro CSP for the owner-operated round trip.

This avoids making `cryptcp` a prerequisite for the first experiment. `cryptcp` remains a valid future production option, but on Windows it has separate licensing from CryptoPro CSP and therefore is not needed merely to prove the existing Rutoken/CryptoPro path.

Canonical detached-signing semantics used by the script:

```text
csptest -sfsign -sign -detached -add -in SHA256SUMS.txt -out SHA256SUMS.txt.sig -my <thumbprint>
csptest -sfsign -verify -detached -in SHA256SUMS.txt -signature SHA256SUMS.txt.sig
```

The signer certificate is included in the CMS/PKCS#7 object with `-add` so the evidence is self-describing enough for the governed verification workflow.

## 7. Acceptance criteria

### Repository implementation

- [x] Windows is selected as the primary owner-operated POC host.
- [x] No exportable key/PFX workflow is introduced.
- [x] POC runner inventories CryptoPro and certificates.
- [x] Code Signing EKU is explicitly inspected.
- [x] Runner creates a disposable release-style SHA-256 manifest.
- [x] Runner supports real detached CryptoPro signing through the selected certificate.
- [x] Runner verifies the detached signature using CryptoPro.
- [x] Runner exports only the public certificate.
- [x] Runner writes non-secret machine-readable evidence.
- [x] Production signing remains disabled.

### Owner-operated closure

- [ ] Run Inspect mode on the Windows notebook with the configured CryptoPro/Rutoken environment.
- [ ] Record the intended ООО «Арвектум» certificate thumbprint and profile.
- [ ] Run the real detached-signature round trip with the Rutoken physically attached.
- [ ] Confirm CryptoPro verification PASS.
- [ ] Review `signing-evidence.json` and confirm no secret material is present.
- [ ] Record whether Code Signing EKU is present or absent.
- [ ] If EKU is absent, formally classify the current УКЭП as **release-evidence only**.
- [ ] If EKU is present, open a separate governed embedded-signing/timestamp/provider-policy probe before any production use.

## 8. Expected likely outcome

The architecture intentionally expects that the existing ordinary qualified certificate may be perfectly suitable for detached qualified release evidence while **not** being a Windows code-signing certificate.

That outcome is a successful POC, not a failure:

```text
Rutoken/CryptoPro detached evidence: PASS
Current УКЭП as Authenticode identity: NOT ELIGIBLE / NOT PROVEN
Production Russian code signing: waits for ОТУЦ or equivalent approved domestic code-signing identity
```

## 9. Closure evidence to retain

After the owner-operated run, retain outside Git until reviewed:

```text
SHA256SUMS.txt
SHA256SUMS.txt.sig
signer-certificate.cer
signing-evidence.json
```

The final closure note for APL-REL-010 must record:

- Windows host used;
- CryptoPro version;
- Rutoken/provider path observed;
- signer subject/thumbprint;
- detached signing result;
- detached verification result;
- Code Signing EKU result;
- final classification of the current certificate;
- whether APL-REL-011 must focus on production release integration or on obtaining/testing the Russian code-signing identity first.

## 10. External basis checked on 2026-08-16

- CryptoPro documents `cryptcp` as a CMS/PKCS#7 signing tool that requires CryptoPro CSP and notes separate Windows licensing for `cryptcp`.
- Rutoken documentation provides a Windows SignTool path for certificates registered through a supported CSP/provider.
- CryptoPro's 2026 ОТУЦ material states that the domestic code-signing infrastructure is intended to address software-distribution trust and that the sector-wide system has been operating in test mode rather than being assumed universally production-ready.

## 11. Next task

After the real hardware run closes this task:

**APL-REL-011 — Russian signed-release integration / OТУЦ readiness**

Exact scope depends on the evidence:

- if the current УКЭП is release-evidence only: integrate qualified detached signing of final release manifests and separately pursue ОТУЦ code-signing enrollment/readiness;
- if a valid code-signing profile unexpectedly exists: perform a separately governed embedded PE/timestamp/trust POC before activation.
