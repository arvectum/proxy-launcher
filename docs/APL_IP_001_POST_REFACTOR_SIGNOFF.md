# APL-IP-001 — post-refactor human/legal sign-off record

Status: **CONDITIONAL — REVIEW PACK COMPLETE / AUTHORIZED SIGNATURE AND DISTRIBUTION-LICENSE REMEDIATION PENDING**

This is the canonical decision record for the post-refactor candidate. It does not authorize a clean-IP tag until the authorized fields below are completed and the final decision is explicitly `APPROVED`.

## Candidate identity

- Repository: `arvectum/proxy-launcher`
- Product version: `0.2.3`
- Candidate commit: `8ad54018e6d6251c906a06d09fd464c8931c14b2`
- Candidate tree: `eac5db739e7bd3fda595b09b2ec869ad06a87ba3`
- Source provenance manifest SHA-256: `5e33393b0864a7804d4303ee2d5bf64daea36a69f5a40e2c3741d3ed3172815d`
- Build SBOM SHA-256: `fccd5d2d94a4c2f8ebbc9fdde709db5b0fd1ae13f962f9046d706086a345ac4a`
- Review evidence: `docs/evidence/APL_IP_001_POST_REFACTOR_REVIEW_2026-08-22.md`

## Promoted artifact scope for this sign-off

The clean-IP/commercial-distribution decision is scoped to artifacts explicitly cleared below.

- [ ] Windows portable
- [ ] Windows installer
- [ ] Linux Debian `.deb`
- [ ] macOS `.app` / DMG
- [ ] Linux AppImage — **must remain unchecked unless separately cleared for the pinned type-2 runtime and its statically linked third-party obligations**

Until final approval, no unchecked artifact may be represented as covered by this sign-off.

## Automated / engineering evidence

- [x] APL-IP-003 engineering refactor complete; Slices 1–23 merged.
- [x] Exact post-refactor candidate selected.
- [x] Candidate provenance artifact regenerated.
- [x] Candidate build SBOM regenerated and reconciled to `requirements-build.lock.txt`.
- [x] Candidate automated provenance-marker findings: `0`.
- [x] Candidate Windows full suite/build/package lifecycle passes; sealed version remains `0.2.3`.
- [x] Cross-platform package/regression evidence survives the refactor.
- [x] Historical Git provenance preserved; human history normalized by `.mailmap`, AI/automation identities not falsified.
- [x] Bounded public-similarity review found no identifiable external exact-source match for the representative high-information source set.

Automated evidence is supporting evidence only and does not establish legal authorship or company title by itself.

## Human factual provenance

The pre-existing factual confirmation in `docs/evidence/APL_IP_001_HUMAN_FACT_CONFIRMATION_2026-08-21.md` records one human developer/project owner behind the `arvectum` / `arutyunoveth` identities, human review/acceptance or correction of AI-assisted source, no deliberate external-project copying, and self-authorship of the base Arvectum logo/monogram.

Authorized reviewer confirmation that these facts remain accurate for the post-refactor candidate:

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

Finding `L-1` in the post-refactor review remains open until the promoted release set contains and verifies the complete license/copyright notices required for the exact shipped third-party payload.

- [ ] Complete third-party license/notice bundle prepared
- [ ] Windows portable payload reconciled to bundle
- [ ] Windows installer payload reconciled to bundle
- [ ] Linux `.deb` payload reconciled to bundle
- [ ] macOS `.app`/DMG payload reconciled to bundle
- [ ] No bundled/frozen third-party component is represented as Arvectum-authored source

Compliance/remediation evidence reference: ______________________________________
Verified by: __________________________________________________________________
Date: _________________________________________________________________________

### AppImage

Current decision: **EXCLUDED / HOLD**.

The pinned type-2 runtime includes statically linked third-party components, including libfuse under LGPL terms. AppImage may be added to the promoted scope only after a separate downstream compliance review/bundle is recorded here:

AppImage clearance reference: __________________________________________________

## Open findings

| ID | Finding | Current status | Closure evidence |
|---|---|---|---|
| R-1 | Executed author -> ООО rights basis | PENDING | __________________ |
| R-2 | Rospatent registration/transfer factual status | PENDING | __________________ |
| R-3 | Corporate/interested-transaction basis where applicable | PENDING | __________________ |
| L-1 | Complete third-party license/notice bundle for promoted artifacts | PENDING | __________________ |
| L-2 | AppImage downstream compliance | EXCLUDED / HOLD | __________________ |

## Final decision

Select exactly one only after all blockers for the selected promoted artifact scope are resolved:

- [ ] **APPROVED** — candidate/title/provenance and selected promoted artifact distribution obligations reviewed; no unresolved blocker remains.
- [ ] **CONDITIONAL** — remediation remains mandatory before tagging/release.
- [ ] **HOLD** — unresolved provenance/license/ownership issue blocks the selected scope.

Current machine-assisted review verdict before authorized signature: **CONDITIONAL**.

Authorized reviewer / authority: _______________________________________________
Review date: __________________________________________________________________
Decision/signature reference: __________________________________________________

## Clean-IP tag authorization

A clean-IP tag may be created only when:

1. this record explicitly selects `APPROVED`;
2. the authorized reviewer/date/signature reference fields are completed;
3. every finding blocking the selected promoted artifact scope is closed;
4. the tag points to the exact reviewed candidate/release commit covered by the evidence.

Until then: **NO CLEAN-IP TAG AUTHORIZED**.
