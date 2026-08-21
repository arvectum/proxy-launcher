# APL-IP-001 — carry-forward closure

Date: 2026-08-21  
Status: **AUTONOMOUS CARRY-FORWARD CLOSURE COMPLETE / HUMAN-LEGAL EXECUTION PENDING**

This record closes the work that can truthfully be completed autonomously before APL-IP-003. It preserves the existing pre-refactor IP evidence, closes the remaining repository-level platform/license packaging gaps, and narrows the unresolved chain-of-title boundary to work that requires an authorized human/legal act.

It is **not** a clean-IP approval, a legal opinion, a signature, or a replacement for the post-refactor review.

## 1. Preserved historical evidence

The following pre-refactor review identity remains immutable evidence and is not rewritten by this closure:

- review candidate commit: `7c3bdbd005e6ff27db8f5a00071dc81c8595dd9b`;
- candidate tree: `9c372b440919b3b9e69d78ab0a85dca3f387d5af`;
- source provenance workflow run: `32409782542`;
- source provenance artifact: `9421664020`;
- source provenance manifest SHA-256: `7b1f42a124c1b0cf068937bb3bb8554609ab7294eb68583ba577b7ead93f1927`;
- build SBOM workflow run: `32409782544`;
- build SBOM artifact: `9421675129`;
- build SBOM SHA-256: `fccd5d2d94a4c2f8ebbc9fdde709db5b0fd1ae13f962f9046d706086a345ac4a`;
- automated provenance findings: `0`;
- governed records: `315`;
- significant product-source records: `34`.

The exact sealed Windows `0.2.3` release remains a historical behavioural/release baseline and is not rebuilt or relabelled by APL-IP-001 closure.

## 2. Human factual provenance already recorded

`docs/evidence/APL_IP_001_HUMAN_FACT_CONFIRMATION_2026-08-21.md` already records the factual human confirmations required for carry-forward:

- the historical `arvectum` / `arutyunoveth` human Git identities map to one human developer/project owner;
- OpenAI remains an AI/tool identity and GitHub Actions remains automation;
- the base Arvectum logo/monogram was confirmed self-authored by the project owner;
- deliberate copying from external projects was denied;
- AI-generated code was human-reviewed and accepted and/or corrected before inclusion.

No history rewrite or author relabelling is permitted to improve the appearance of provenance.

## 3. Repository-level platform/license gap closed

Canonical reconciliation record:

`docs/evidence/APL_IP_001_PLATFORM_LICENSE_RECONCILIATION_2026-08-21.md`

Carry-forward hardening adds enforceable package-notice delivery:

- Linux `.deb`: existing `LICENSE` + `THIRD_PARTY_NOTICES.txt` package contract retained;
- Linux AppImage: product license and third-party notices now installed into the AppDir and protected by a packaging test;
- macOS `.app`: product license and third-party notices now copied into `Contents/Resources` and protected by a packaging test;
- macOS DMG: the same notices are additionally exposed at DMG root and protected by a packaging test;
- Windows: existing Russian-first exact release ceremony already requires and stages the notice/license files beside the exact sealed portable ZIP and installer.

The AppImage runtime's transitive static-link license obligations are intentionally **not** hidden. AppImage remains an optional bounded distribution hold until those obligations are reviewed/satisfied for a production AppImage release. The preferred controlled Linux/Astra lane remains `.deb`.

These hardening changes post-date the historical candidate. They are forward changes to be retained by APL-IP-003 and reviewed again in the new post-refactor candidate; they are not retroactively attributed to `7c3bdbd...`.

## 4. Build-SBOM boundary closed

`.github/workflows/sbom.yml` already creates and validates a reproducible CycloneDX 1.6 SBOM from `requirements-build.lock.txt`. APL-IP-001 now records explicitly that this is a **build-dependency SBOM** and must not be misrepresented as a universal final-payload SBOM.

This resolves the ambiguity without fabricating binary-level artifact evidence that does not exist.

## 5. Chain-of-title boundary

The repository-side author-to-company instrument is prepared at:

`docs/legal/APL_IP_001_RIGHTS_ASSIGNMENT_TEMPLATE.md`

What automation can do is complete: identify the source scope, candidate, provenance evidence, contributor identity mapping and document template.

What automation cannot truthfully do is still pending:

1. an authorized human must execute the author → ООО «Арвектум» rights instrument (or document an independently verified equivalent existing rights basis);
2. the confidential executed original may remain outside the public repository, but the repository must record a stable non-secret evidence reference, date, scope and verifier;
3. a later authorized reviewer must make the final legal/commercial-distribution decision against the **post-refactor** candidate.

No signature, authority, contractual fact or legal approval is invented by this closure.

## 6. Pre-refactor clean-IP tag decision

**DO NOT CREATE A PRE-REFACTOR CLEAN-IP TAG.**

The pre-refactor candidate is retained as provenance/history evidence only. A clean-IP tag is deliberately reserved for the new canonical source edition after APL-IP-003, regeneration of provenance/SBOM evidence, exact payload/license review, and explicit APPROVED status.

This avoids spending a clean-IP baseline on a tree that is immediately scheduled for canonical refactor.

## 7. Carry-forward acceptance

Autonomous/repository acceptance:

- [x] exact historical candidate/evidence preserved;
- [x] automated provenance findings dispositioned;
- [x] human factual provenance confirmation preserved;
- [x] build SBOM boundary explicitly classified;
- [x] Windows release-set notice/license delivery bound to existing evidence;
- [x] Linux `.deb` notice/license packaging contract preserved;
- [x] AppImage notice/license packaging gap remediated and test-protected;
- [x] macOS `.app`/DMG notice/license packaging gap remediated and test-protected;
- [x] AppImage transitive-license risk bounded rather than falsely approved;
- [x] author-to-company rights instrument prepared;
- [x] no pre-refactor clean-IP tag created;
- [ ] executed author-to-ООО rights evidence reference — **HUMAN/LEGAL ACTION REQUIRED**;
- [ ] final post-refactor APPROVED decision/tag — **DEFERRED BY SEQUENCING**.

## 8. Exit state

APL-IP-001 carry-forward is **autonomously closed**. The remaining pre-APL-IP-003 boundary is a named human/legal execution step, not unfinished repository engineering.

After the executed rights-basis evidence reference exists, proceed to APL-IP-003. After APL-IP-003, select one new exact candidate and perform the final source/provenance/SBOM/platform-license/human/legal review before creating any clean-IP tag.
