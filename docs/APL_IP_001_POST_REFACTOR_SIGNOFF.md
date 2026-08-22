# APL-IP-001 — post-refactor human/legal sign-off record

Status: **CONDITIONAL — POST-APL-IP-004 ENGINEERING RECONCILED / AUTHORIZED HUMAN-LEGAL SIGN-OFF PENDING**

This is the canonical decision record for the current APL-IP-001 candidate. It does not authorize a clean-IP tag until the authorized fields below are completed and the final decision is explicitly `APPROVED`.

## Candidate identity

- Repository: `arvectum/proxy-launcher`
- Product version: `0.2.3`
- Immutable APL-IP-003/source-review anchor commit: `8ad54018e6d6251c906a06d09fd464c8931c14b2`
- Immutable APL-IP-003/source-review anchor tree: `eac5db739e7bd3fda595b09b2ec869ad06a87ba3`
- Selected post-APL-IP-004 candidate commit: `ef9846e151a2e4e7046169e0787603969018cc97`
- Selected candidate tree: `98a09d821470a597715696e5ff3c7f376e5893a8`
- Candidate-equivalent validated PR head: `ab3f6aea8087ac09c3d8dcbdf348fcc7f6684f9f`
- Candidate-equivalent PR test-merge: `818a39591cd2377bd1c451294854d4f787a9f369`
- Source provenance manifest SHA-256: `baf27272def4c03c7f44852ff11aa1c2fdb32710f92ac0e322f94b557158a87b`
- Build SBOM SHA-256: `fccd5d2d94a4c2f8ebbc9fdde709db5b0fd1ae13f962f9046d706086a345ac4a`
- Source-review evidence: `docs/evidence/APL_IP_001_POST_REFACTOR_REVIEW_2026-08-22.md`
- Post-APL-IP-004 reconciliation evidence: `docs/evidence/APL_IP_001_POST_IP_004_CANDIDATE_RECONCILIATION_2026-08-22.md`

The validated PR head, PR test-merge and selected final merge candidate have the identical tree `98a09d821470a597715696e5ff3c7f376e5893a8`. The post-APL-IP-004 evidence is therefore candidate-content exact even though the Git merge topology differs.

## Promoted artifact scope for final sign-off

The final clean-IP/commercial-distribution decision is scoped only to artifacts explicitly selected by the authorized reviewer below. Engineering readiness does not select or legally approve an artifact by itself.

- [ ] Windows portable
- [ ] Windows installer
- [ ] Linux Debian `.deb`
- [ ] macOS `.app` / DMG
- [ ] Linux AppImage — **must remain unchecked unless separately cleared for the pinned type-2 runtime and its statically linked third-party obligations**

Until final approval, no unchecked artifact may be represented as covered by this sign-off.

## Automated / engineering evidence

- [x] APL-IP-003 engineering refactor complete; Slices 1–23 merged.
- [x] Exact post-APL-IP-004 candidate selected.
- [x] Candidate-equivalent PR tree and final merge tree proven identical.
- [x] Candidate provenance artifact regenerated: 377 governed records, 45 product-source records, automated provenance-marker findings `0`.
- [x] Candidate build SBOM regenerated and reconciled to `requirements-build.lock.txt`.
- [x] No product-source file in the 45-file post-refactor significant-source set changed between the source-review anchor and the selected post-APL-IP-004 candidate.
- [x] Bounded public-similarity/source review is therefore carried forward only for the unchanged product-source set, not falsely regenerated for packaging-only changes.
- [x] APL-IP-004 full third-party license bundle control is implemented and accepted for newly built Windows portable, Windows installer, Debian `.deb`, and macOS `.app`/DMG lanes.
- [x] Windows portable promoted-license gate passes on candidate-equivalent tree.
- [x] Windows installer fresh/upgrade/repair/uninstall and Gate R6 acceptance pass on candidate-equivalent tree after explicit rerun of the concurrency-cancelled job.
- [x] Debian packaging passes on Ubuntu 22.04 and 24.04 with generated/verified bundle included in package documentation payload.
- [x] macOS Apple Silicon and Intel `.app`/DMG packaging passes with generated/verified bundle and DMG integrity inspection.
- [x] Historical Git provenance preserved; human history normalized by `.mailmap`, AI/automation identities not falsified.
- [x] AppImage remains explicitly excluded from promoted commercial scope pending separate L-2 clearance.

Automated evidence is supporting evidence only and does not establish legal authorship, company title or legal/commercial approval by itself.

## Human factual provenance

The pre-existing factual confirmation in `docs/evidence/APL_IP_001_HUMAN_FACT_CONFIRMATION_2026-08-21.md` records one human developer/project owner behind the `arvectum` / `arutyunoveth` identities, human review/acceptance or correction of AI-assisted source, no deliberate external-project copying, and self-authorship of the base Arvectum logo/monogram.

The 45-file product-source set is unchanged from the post-refactor source-review anchor, but the selected candidate identity changed after APL-IP-004. Authorized reviewer confirmation is therefore still required that the carried-forward facts remain accurate for candidate `ef9846e151a2e4e7046169e0787603969018cc97`:

- [ ] Confirmed without correction
- [ ] Corrected/supplemented in evidence reference: ______________________________

Reviewer: ______________________________
Date: __________________________________

## Author -> ООО «Арвектум» chain of title

An executed rights basis must be verified rather than inferred from Git authorship.

- [ ] Executed written author -> ООО rights instrument verified
- [ ] Alternative valid existing rights basis verified

Stable non-secret evidence reference: ___________________________________________
Execution/effective date: ______________________________________________________
Scope/candidate covered: _______________________________________________________
Verified by: __________________________________________________________________

The executed instrument or alternative basis must cover the selected post-APL-IP-004 candidate identity above. A draft that names only the older `8ad54018...` source-review anchor is not sufficient for R-1 closure without an explicit valid extension/superseding instrument.

If a signed agreement is used, the public repository should record a stable internal reference rather than publishing confidential originals/personal data.

## Rospatent registration status

The repository itself does not establish whether the program is registered. Authorized factual confirmation is required.

Choose exactly one:

- [ ] Program is not registered in Rospatent as of review date
- [ ] Program is registered; registration/certificate reference: __________________

If registered and the exclusive right is transferred, required transfer-registration reference/status:

________________________________________________________________________________

Verified by: ______________________________
Date: _____________________________________

## Corporate transaction / interested-person basis

Where the individual author is also a director, participant, controlling person or otherwise interested in the author -> ООО transaction, record the company's actual corporate-law basis rather than assuming an exception.

Choose/document as applicable:

- [ ] No interested-person corporate approval issue applies; basis: ______________
- [ ] Applicable statutory/charter exception verified; basis: ____________________
- [ ] Required corporate consent/approval obtained; reference: ___________________

Verified by: ______________________________
Date: _____________________________________

## Third-party distribution license reconciliation

Finding `L-1` from the post-refactor review is now **ENGINEERING-REMEDIATED** for newly built promoted Windows portable, Windows installer, Debian `.deb`, and macOS `.app`/DMG artifacts under APL-IP-004. This engineering closure does not itself select those artifacts for final legal/commercial approval.

- [x] Complete third-party license/notice bundle generation and fail-closed verification implemented
- [x] Windows portable payload reconciled to bundle
- [x] Windows installer payload reconciled to bundle
- [x] Linux `.deb` payload reconciled to bundle
- [x] macOS `.app`/DMG payload reconciled to bundle
- [x] No bundled/frozen third-party component is represented as Arvectum-authored source

Compliance/remediation evidence reference: `docs/evidence/APL_IP_001_POST_IP_004_CANDIDATE_RECONCILIATION_2026-08-22.md`  
Engineering control: `docs/APL_IP_004_THIRD_PARTY_LICENSE_BUNDLE_PROMOTED_ARTIFACT_COMPLIANCE.md`  
Machine-assisted reconciliation date: `2026-08-22`

### AppImage

Current decision: **EXCLUDED / HOLD**.

The pinned type-2 runtime includes statically linked third-party components, including libfuse under LGPL terms. AppImage may be added to the promoted scope only after a separate downstream compliance review/bundle is recorded here:

AppImage clearance reference: __________________________________________________

## Open findings

| ID | Finding | Current status | Closure evidence |
|---|---|---|---|
| R-1 | Executed author -> ООО rights basis | PENDING / HUMAN | __________________ |
| R-2 | Rospatent registration/transfer factual status | PENDING / HUMAN | __________________ |
| R-3 | Corporate/interested-transaction basis where applicable | PENDING / HUMAN | __________________ |
| L-1 | Complete third-party license/notice bundle for promoted artifacts | ENGINEERING-REMEDIATED | `docs/evidence/APL_IP_001_POST_IP_004_CANDIDATE_RECONCILIATION_2026-08-22.md` |
| L-2 | AppImage downstream compliance | EXCLUDED / HOLD | separate clearance required |

## Final decision

Select exactly one only after all human/legal blockers for the selected promoted artifact scope are resolved:

- [ ] **APPROVED** — candidate/title/provenance and selected promoted artifact distribution obligations reviewed; no unresolved blocker remains.
- [ ] **CONDITIONAL** — remediation or authorized factual/legal execution remains mandatory before tagging/release.
- [ ] **HOLD** — unresolved provenance/license/ownership issue blocks the selected scope.

Current machine-assisted review verdict before authorized signature: **CONDITIONAL**.

Reason for current `CONDITIONAL`: R-1, R-2, R-3, post-candidate human factual confirmation and authorized final decision remain pending. L-1 is no longer an engineering blocker for the four non-AppImage promoted lanes listed above.

Authorized reviewer / authority: _______________________________________________
Review date: __________________________________________________________________
Decision/signature reference: __________________________________________________

## Clean-IP tag authorization

A clean-IP tag may be created only when:

1. this record explicitly selects `APPROVED`;
2. the authorized reviewer/date/signature reference fields are completed;
3. every finding blocking the selected promoted artifact scope is closed;
4. the tag points to the exact reviewed candidate/release commit covered by the evidence;
5. no product source, build dependency, packaging/compliance implementation or selected promoted-artifact contents have changed after the selected candidate without a new exact reconciliation.

Until then: **NO CLEAN-IP TAG AUTHORIZED**.
