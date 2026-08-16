# APL-REL-013 — Russian production release gate

**Status:** IMPLEMENTED / REPOSITORY COMPLETE / MUST RUN FOR EVERY PRODUCTION RELEASE  
**Decision date:** 2026-08-16  
**Primary market:** Russian Federation  
**Owner:** ООО «Арвектум»

## 1. Goal

APL-REL-013 turns the Russia-first release chain into a single fail-closed publication decision.

The preceding tasks established:

```text
APL-REL-010
  real Rutoken/CryptoPro hardware POC
  governed ООО «Арвектум» certificate
  release-evidence-only classification

APL-REL-011
  final assets -> SHA256SUMS.txt
  -> detached CryptoPro/Rutoken signature
  -> signer-certificate.cer
  -> signing-evidence.json

APL-REL-012
  end-user verifier
  -> asset SHA-256 verification
  -> detached CryptoPro verification
  -> governed signer binding
  -> Russian PASS/FAIL UX
```

APL-REL-013 answers the final operational question:

> **Можно ли публиковать этот конкретный релиз?**

There are only two valid outcomes:

```text
PUBLISH
НЕ ПУБЛИКОВАТЬ
```

Any missing, inconsistent or unproven condition is `НЕ ПУБЛИКОВАТЬ`.

## 2. Canonical gate

```text
tools/russian_production_release_gate.ps1
```

The gate must run on Windows against the exact final directory that is intended for publication.

It does not build or sign a release. It is deliberately downstream of the owner-operated REL-011 ceremony.

## 3. Required input state

The final release directory must already contain at least:

```text
<product release asset(s)>
verify_russian_release.ps1
VERIFY_RUSSIAN_RELEASE.cmd
SHA256SUMS.txt
SHA256SUMS.txt.sig
signer-certificate.cer
signing-evidence.json
```

The verifier UX must have been copied into the directory **before** REL-011 signing, so both consumer verification files are themselves covered by the signed manifest.

## 4. What the gate proves

APL-REL-013 fails closed unless all of the following are true:

1. The run is on Windows.
2. The supplied `Version`, `GitTag` and `GitCommit` are mutually consistent.
3. `signing-evidence.json` identifies `Arvectum Proxy Launcher`.
4. The evidence was produced by `APL-REL-011` in `russian-qualified-evidence` mode.
5. Evidence version/tag/commit exactly match the requested production release.
6. REL-011 records successful detached-signature verification.
7. Evidence does not report PIN storage or private-key export attempts.
8. The signer thumbprint is the currently governed ООО «Арвектум» release-evidence certificate:

```text
EE1CFA955BA22F03C39C76B183D94CD37494582E
```

9. The signer subject identifies `АРВЕКТУМ`.
10. The complete untouched final release directory passes the bundled REL-012 verifier.
11. The current Git `HEAD` is exactly the release commit.
12. The requested Git tag resolves exactly to that commit.
13. The release commit is an ancestor of canonical local `main`.
14. The Git worktree is clean.
15. A disposable copy of the release is modified and the bundled REL-012 verifier rejects it.
16. No ungoverned Authenticode/SmartScreen claim is promoted by the gate.

Only after all checks pass may the gate emit `PUBLISH`.

## 5. Mandatory negative tamper test

A positive verifier result alone is not enough for the production gate.

APL-REL-013 copies the exact final release to a temporary directory, changes one signed asset and executes the **bundled** `verify_russian_release.ps1` against that tampered copy.

Expected result:

```text
REL-012 original exact final set: PASS
REL-012 tampered disposable copy: FAIL
APL-REL-013 interpretation: PASS
```

If the tampered copy is accepted, the production decision is automatically:

```text
НЕ ПУБЛИКОВАТЬ
```

The original release directory is never modified by this test.

## 6. Git provenance boundary

The production package must be traceable to one exact approved repository state.

The gate requires:

```text
HEAD == GitCommit
GitTag^{commit} == GitCommit
GitCommit is ancestor of main
worktree == clean
```

This prevents a production release from being approved from an uncommitted local patch, the wrong tag, or a branch state not represented by canonical `main`.

## 7. Publication-decision evidence

After PASS, the gate writes a non-secret machine-readable decision file named by default:

```text
<release-directory-name>.production-release-gate.json
```

It is deliberately written **outside** the signed release directory.

Putting it inside the final directory after REL-011 signing would add an unlisted file and invalidate REL-012 verification. The gate explicitly rejects an output path inside the signed release set.

The decision record contains:

```text
task = APL-REL-013
decision = PUBLISH
version / git_tag / git_commit
signer identity
REL-011 detached-signature status
REL-012 exact-release PASS
REL-012 negative-tamper expected FAIL
git/tag/main/worktree checks
explicit false values for Authenticode/SmartScreen claims
```

This JSON is release-operation evidence, not a new cryptographic trust anchor.

## 8. Canonical owner-operated sequence

For **каждого релиза** intended for Russian production publication:

```powershell
# 1. Build the exact final product assets.

# 2. Add the consumer verifier before signing.
powershell -ExecutionPolicy Bypass -File .\tools\prepare_russian_release_verification_ux.ps1 `
  -ReleaseDirectory "C:\release\Arvectum-Proxy-Launcher-1.0.0"

# 3. Run REL-011 owner-operated Rutoken/CryptoPro signing.
powershell -ExecutionPolicy Bypass -File .\tools\russian_signed_release.ps1 `
  -ReleaseDirectory "C:\release\Arvectum-Proxy-Launcher-1.0.0" `
  -Version "1.0.0" `
  -GitTag "v1.0.0" `
  -GitCommit "<40-character-main-commit>" `
  -CertificateThumbprint "EE1CFA955BA22F03C39C76B183D94CD37494582E"

# 4. Run the final production gate.
powershell -ExecutionPolicy Bypass -File .\tools\russian_production_release_gate.ps1 `
  -ReleaseDirectory "C:\release\Arvectum-Proxy-Launcher-1.0.0" `
  -Version "1.0.0" `
  -GitTag "v1.0.0" `
  -GitCommit "<40-character-main-commit>"
```

Publication is permitted only if the final command prints:

```text
APL-REL-013 Russian production release gate: PASS
Publication decision: PUBLISH
REL-012 exact final set verification: PASS
Negative tamper test: PASS (tampered copy correctly rejected)
```

## 9. Mandatory НЕ ПУБЛИКОВАТЬ conditions

Do not publish if any of these conditions is true:

- REL-011 owner-operated signing did not complete successfully;
- REL-012 verification fails on the exact final download set;
- a signed asset is missing, changed or extra;
- the manifest, detached signature or exported certificate is inconsistent;
- the signer is not the governed Arvectum certificate;
- version/tag/commit metadata disagree;
- the local tag points to another commit;
- HEAD differs from the release commit;
- the release commit is not represented by canonical `main`;
- the worktree contains uncommitted changes;
- the negative tamper copy unexpectedly verifies successfully;
- evidence reports PIN storage or a private-key export attempt;
- release notes claim Authenticode, SmartScreen or Windows trusted-publisher status that has not been separately proven.

## 10. Authenticode / SmartScreen boundary

The current governed certificate proved by APL-REL-010 has no Code Signing EKU and remains classified:

```text
RELEASE-EVIDENCE-ONLY
```

Therefore APL-REL-013 does **not** claim:

```text
Authenticode signed
SmartScreen trusted
Windows trusted publisher
Microsoft trusted
ОТУЦ code-signed
```

A Russian release may be cryptographically verifiable and permitted for publication by this gate without possessing those separate OS-native trust properties.

## 11. CI boundary

Workflow:

```text
.github/workflows/russian-production-release-gate.yml
```

CI validates only the repository contract and PowerShell syntax. It deliberately has:

- no Rutoken;
- no CryptoPro production identity;
- no certificate private key;
- no PIN;
- no production signing secret.

CI cannot issue `PUBLISH` for a real production release. Only the owner-operated Windows ceremony against the exact final release set can do that.

## 12. Acceptance checklist

Repository implementation:

- [x] Fail-closed production gate implemented.
- [x] REL-011 evidence chain required.
- [x] REL-012 exact-final-set verification required.
- [x] Governed Arvectum signer pinned.
- [x] Version/tag/commit binding implemented.
- [x] Exact HEAD and tag target enforced.
- [x] Canonical `main` ancestry enforced.
- [x] Clean worktree enforced.
- [x] Mandatory disposable negative tamper test implemented.
- [x] Decision evidence kept outside signed release directory.
- [x] Authenticode/SmartScreen overclaiming prevented.
- [x] Non-secret CI contract and PowerShell syntax validation defined.

Per-release owner operation:

- [ ] Build exact final assets.
- [ ] Bundle REL-012 UX before signing.
- [ ] Run REL-011 with physical Rutoken/CryptoPro and receive PASS.
- [ ] Create/resolve the exact release tag to the exact release commit.
- [ ] Run APL-REL-013 against the exact final download set.
- [ ] Receive `Publication decision: PUBLISH`.
- [ ] Preserve the external `production-release-gate.json` with release records.
- [ ] Publish only that exact verified release set.

## 13. Completion definition

APL-REL-013 repository implementation is complete when the gate script, contract tests, documentation and CI syntax checks are merged to `main`.

A specific product version becomes a **production-approved Russian release** only after its own owner-operated REL-011 + REL-012 + REL-013 ceremony returns PASS.
