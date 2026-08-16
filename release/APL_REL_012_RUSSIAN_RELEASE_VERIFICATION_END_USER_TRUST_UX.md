# APL-REL-012 — Russian release verification & end-user trust UX

**Status:** IMPLEMENTED / REPOSITORY COMPLETE / REAL RELEASE CEREMONY STILL REQUIRED PER VERSION  
**Decision date:** 2026-08-16  
**Primary market:** Russian Federation  
**Owner:** ООО «Арвектум»

## 1. Goal

APL-REL-011 established the Russia-first release-evidence path:

```text
final release assets
  -> SHA256SUMS.txt
  -> detached CryptoPro/Rutoken signature
  -> signer-certificate.cer
  -> signing-evidence.json
```

APL-REL-012 makes that evidence usable by an ordinary Windows customer and prevents the product from overstating what has actually been proven.

The end-user verification path must answer three different questions independently:

1. **Криптографическая целостность** — совпадают ли SHA-256 хэши скачанных файлов с подписанным манифестом.
2. **Подлинность релиза** — действительно ли `SHA256SUMS.txt` подписан утверждённым сертификатом ООО «Арвектум» и проходит проверку CryptoPro.
3. **OS-native publisher trust** — считает ли сама ОС исполняемый файл нативно подписанным доверенным издателем (например, Authenticode/SmartScreen в Windows).

A successful result for items 1 and 2 does **not** silently imply item 3.

## 2. Consumer files

Canonical verifier:

```text
tools/verify_russian_release.ps1
```

One-click Windows launcher:

```text
tools/VERIFY_RUSSIAN_RELEASE.cmd
```

Release-preparation helper:

```text
tools/prepare_russian_release_verification_ux.ps1
```

The preparation helper copies the two consumer verification files into the final release directory **before** `tools/russian_signed_release.ps1` runs. They therefore become normal release assets covered by `SHA256SUMS.txt` and by the detached qualified signature.

## 3. Publisher sequence

For every Russian release, use this order:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\prepare_russian_release_verification_ux.ps1 `
  -ReleaseDirectory "C:\release\Arvectum-Proxy-Launcher-1.0.0"

powershell -ExecutionPolicy Bypass -File .\tools\russian_signed_release.ps1 `
  -ReleaseDirectory "C:\release\Arvectum-Proxy-Launcher-1.0.0" `
  -Version "1.0.0" `
  -GitTag "v1.0.0" `
  -GitCommit "<40-character-approved-main-commit>" `
  -CertificateThumbprint "EE1CFA955BA22F03C39C76B183D94CD37494582E"
```

Publication is allowed only after the owner-operated signing command itself returns PASS.

The final directory must contain at least:

```text
<product release asset(s)>
verify_russian_release.ps1
VERIFY_RUSSIAN_RELEASE.cmd
SHA256SUMS.txt
SHA256SUMS.txt.sig
signer-certificate.cer
signing-evidence.json
```

Both verifier files must appear in `SHA256SUMS.txt` because they are copied before the signing ceremony.

## 4. Simplest user instruction

For a Windows user with CryptoPro CSP already installed:

1. Download the **whole release set from the same official Arvectum release**. Do not mix files from different versions.
2. Keep the files in one folder.
3. Double-click `VERIFY_RUSSIAN_RELEASE.cmd`.
4. Read the final status.
5. Launch/install the product only if the tool prints:

```text
РЕЗУЛЬТАТ: ПРОВЕРКА ПРОЙДЕНА
Криптографическая целостность: ПОДТВЕРЖДЕНА
Detached CryptoPro signature: ПОДТВЕРЖДЕНА
Подлинность российского release manifest: ПОДТВЕРЖДЕНА
```

If the result is `ПРОВЕРКА НЕ ПРОЙДЕНА`, the UX explicitly tells the user not to execute the release files.

## 5. What the verifier checks

`verify_russian_release.ps1` fails closed unless all of the following are true:

- Windows is being used;
- CryptoPro CSP `csptest.exe` is available;
- all four REL-011 evidence files are present;
- `signing-evidence.json` identifies `Arvectum Proxy Launcher` and `russian-qualified-evidence` mode;
- the release evidence does not claim embedded code signing;
- the SHA-256 of `SHA256SUMS.txt` matches the evidence record;
- the SHA-256 of `SHA256SUMS.txt.sig` matches the evidence record;
- every manifest line is syntactically valid;
- manifest paths cannot be absolute, nested or traversal paths;
- duplicate manifest filenames are rejected;
- every listed release asset exists and its SHA-256 matches;
- unexpected unlisted files are rejected (except the four canonical evidence files);
- evidence asset hashes agree with the manifest;
- CryptoPro positively verifies the detached CMS/PKCS#7 signature;
- the CMS contains exactly one signer certificate;
- the certificate **inside the CMS signature** has the governed thumbprint;
- the exported `signer-certificate.cer` matches the CMS signer certificate;
- the signer thumbprint recorded in evidence matches the CMS signer certificate;
- the certificate subject identifies `АРВЕКТУМ`.

The trust decision is therefore not based on `signing-evidence.json` alone. The signer identity is taken from the signed CMS object and compared to the pinned governed certificate.

## 6. Current governed signer

APL-REL-010 proved this real owner-operated identity on 2026-08-16:

```text
Owner: ООО «Арвектум»
Certificate thumbprint: EE1CFA955BA22F03C39C76B183D94CD37494582E
Issuer: Федеральная налоговая служба
Validity: 2026-06-25 to 2027-09-25
CryptoPro detached signing: PASS
CryptoPro detached verification: PASS
Code Signing EKU: ABSENT
Classification: RELEASE-EVIDENCE-ONLY
```

The verifier pins this thumbprint by default. Certificate renewal/replacement is therefore a governed release change: update the approved identity, update the verifier, prove the new path, and only then publish a release using the new certificate.

## 7. Trust UX wording

### Allowed wording after PASS

```text
Целостность файлов релиза подтверждена SHA-256.
Подлинность подписанного манифеста релиза подтверждена CryptoPro.
Подписант: ООО «Арвектум».
```

### Required limitation

The verifier always states that PASS:

```text
НЕ означает, что EXE имеет Microsoft Authenticode-подпись;
НЕ означает репутацию SmartScreen;
НЕ доказывает нативное доверие Windows к издателю.
```

### Forbidden wording under the current certificate

Do not publish claims such as:

```text
Microsoft trusted
SmartScreen trusted
Windows trusted publisher
Authenticode signed
ОТУЦ code-signed
```

until the corresponding exact-release property has separately been proven.

## 8. Why the verifier itself is trustworthy enough for this flow

The user-facing PowerShell verifier and CMD launcher are copied into the release directory before manifest generation. The publisher then signs the manifest that includes their SHA-256 values.

This prevents a post-signing modification of the verifier from passing its own asset-integrity check when the complete official release set is kept together.

For the signer identity, the verifier does not trust a JSON label. It decodes the CMS signer certificate, compares it to the pinned Arvectum thumbprint, compares the exported certificate to that signer, and separately requires CryptoPro to validate the detached signature.

## 9. Failure UX

Any inconsistency results in non-zero exit code and the Russian-language status:

```text
РЕЗУЛЬТАТ: ПРОВЕРКА НЕ ПРОЙДЕНА
Не запускайте файлы из этого релиза до получения исправного пакета из официального канала Арвектум.
```

Typical blocked cases:

- modified EXE/ZIP/installer;
- missing release asset;
- replaced manifest;
- replaced detached signature;
- replaced public certificate;
- signature created by a different certificate;
- mixed evidence from another version;
- extra unlisted executable/file in the release directory;
- malformed or path-traversal manifest entry;
- missing/broken CryptoPro CSP;
- evidence falsely claiming embedded code signing.

## 10. Publication gate

A release must be classified **НЕ ПУБЛИКОВАТЬ** as a verified Russian release if:

- the verification UX was added after signing instead of before signing;
- either verifier file is absent from the signed SHA-256 manifest;
- the owner-operated REL-011 signing ceremony did not PASS;
- `VERIFY_RUSSIAN_RELEASE.cmd` does not produce PASS on the exact final download set;
- any negative tamper test unexpectedly passes;
- the signer thumbprint is not the currently governed Arvectum release-evidence certificate;
- marketing/release notes imply OS-native publisher trust that has not been separately proven.

## 11. CI boundary

Workflow:

```text
.github/workflows/russian-release-verification.yml
```

CI is intentionally non-secret. It:

- runs the REL-012 repository contract tests;
- parses the PowerShell scripts on `windows-latest` to catch syntax errors;
- verifies the pinned identity and fail-closed checks remain in source;
- verifies the Russian UX and non-overclaiming trust wording remain in source.

CI does not possess the Rutoken, certificate private key, PIN, CryptoPro production identity or any signing secret, and it does not create production signatures.

## 12. Real-release acceptance checklist

Repository implementation:

- [x] Russian one-click verification launcher implemented.
- [x] Fail-closed PowerShell verifier implemented.
- [x] SHA-256 verification implemented for every signed asset.
- [x] Unexpected/unlisted release files rejected.
- [x] Detached CryptoPro verification required.
- [x] CMS signer certificate extracted and checked.
- [x] Current governed Arvectum signer thumbprint pinned.
- [x] Exported signer certificate cross-checked with CMS signer.
- [x] Evidence metadata cross-checked but not used as the sole trust anchor.
- [x] Verification UX is bundled before signing so it is itself hashed.
- [x] Russian PASS/FAIL messaging implemented.
- [x] Explicit Authenticode/SmartScreen limitation implemented.
- [x] CI contract and Windows PowerShell syntax check implemented.

Per-release owner operation:

- [ ] Build the exact final release assets.
- [ ] Add REL-012 verifier UX to the final directory.
- [ ] Run REL-011 owner-operated Rutoken/CryptoPro signing.
- [ ] Run `VERIFY_RUSSIAN_RELEASE.cmd` against the exact final download set.
- [ ] Confirm PASS.
- [ ] Modify one disposable copy of an asset and confirm FAIL.
- [ ] Restore/re-download the clean set and confirm PASS again.
- [ ] Publish all assets and evidence together.

## 13. Closure classification

```text
APL-REL-012 repository implementation: PASS
End-user SHA-256 verification path: READY
End-user detached CryptoPro verification path: READY
CMS signer identity binding: READY
Russian-language one-click UX: READY
Current governed signer pinned: YES
Current certificate: RELEASE-EVIDENCE-ONLY
OS-native publisher trust claimed: NO
SmartScreen trust claimed: NO
Embedded Russian code signing activated: NO
Real final-release verification ceremony: REQUIRED PER RELEASE
```
