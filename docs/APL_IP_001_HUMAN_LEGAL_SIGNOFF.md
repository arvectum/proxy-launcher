# APL-IP-001 — human/legal sign-off record

Status: **PENDING AUTHORIZED HUMAN/LEGAL REVIEW**. This record must be completed before a clean IP baseline/tag is created.

Use `docs/APL_IP_001_REVIEW_PACKET.md` as the bounded review guide and `docs/evidence/APL_IP_001_REVIEW_CANDIDATE_2026-08-20.md` as the automated evidence binding. Do not treat CI, hashes, Git authorship, commit metadata or AI tooling as legal proof of authorship or ownership by themselves.

## Candidate identity

- Product version: `0.2.3`
- Candidate commit SHA: `7c3bdbd005e6ff27db8f5a00071dc81c8595dd9b`
- Candidate source tree SHA: `9c372b440919b3b9e69d78ab0a85dca3f387d5af`
- Source provenance artifact/run reference: workflow run `32409782542`, artifact `9421664020`
- Source provenance manifest SHA-256: `7b1f42a124c1b0cf068937bb3bb8554609ab7294eb68583ba577b7ead93f1927`
- Source provenance artifact digest: `528990e85b79a441ad8477451cf0537e47d6f3b5398056d4672d476690407b42`
- Build SBOM artifact/run reference: workflow run `32409782544`, artifact `9421675129`
- Build SBOM SHA-256: `fccd5d2d94a4c2f8ebbc9fdde709db5b0fd1ae13f962f9046d706086a345ac4a`
- Platform payload/release-evidence references: Windows `docs/evidence/WINDOWS_RUSSIAN_PRODUCTION_SIGNING_ACCEPTANCE_2026-08-20.json`; Linux/macOS payload/license reconciliation remains a reviewer checklist item
- `THIRD_PARTY_NOTICES.txt` SHA-256: `c36fab57e42132ebcc4201d681e706dbd6fad3c54630d887aa836d04bd192530`
- Reviewer / authority: _________________________________________
- Review date: __________________________________________________

Automated candidate facts: manifest schema `2`; `315` governed records; `34` product-source records; `0` automated provenance findings; `human_review_required=true`; `legal_signoff_required=true`. The PR head, PR merge-test ref and candidate commit share the same source tree SHA, as recorded in the candidate evidence file.

## Significant-source review

Inspect the exact candidate tree, relevant Git history, the mandatory source list in the review packet and all provenance-manifest review findings.

- [ ] Core/control plane and configuration/state ownership.
- [ ] Windows backend/recovery/diagnostics/release integration.
- [ ] Linux/Astra backend, NetworkManager/PolicyKit, recovery, diagnostics, autostart and packaging glue.
- [ ] macOS backend, `networksetup` preflight, recovery, diagnostics, LaunchAgent and packaging glue.
- [ ] Routing control plane: `routing_rules.py`, `windows_app_routing.py`, `routing_ownership.py`.
- [ ] GUI/failure-state logic and security/privacy boundaries.
- [ ] Build/release/CI scripts that materially affect shipped artifacts or provenance.
- [ ] Visual/brand assets claimed by ООО «Арвектум».
- [ ] Every automated provenance finding is investigated and dispositioned (candidate automated count: `0`; prior false-positive triage is documented in the review packet).
- [ ] Any material AI-assisted or imported/template-like fragment has been human-reviewed and deliberately accepted, rewritten, or separately licensed as appropriate.
- [ ] Human creative contribution is identifiable for material product modules; AI assistance is not represented as a legal author.

Do not delete/rewrite Git history to manufacture provenance or authorship.

### Findings

| Path/module | Finding/source | Review action | Final disposition |
|---|---|---|---|
|  |  |  |  |

## Artifact / third-party reconciliation

The repository CI SBOM is a build-dependency SBOM. Platform payload evidence must be reviewed separately; do not use one build SBOM as a universal shipped-artifact inventory.

- [ ] Build SBOM reconciled with `requirements-build.lock.txt`.
- [ ] Windows portable payload/evidence reconciled with notices/licenses.
- [ ] Windows installer payload/evidence reconciled with notices/licenses.
- [ ] Linux `.deb` payload/evidence reconciled with notices/licenses.
- [ ] Linux AppImage payload/evidence reconciled with notices/licenses, including the pinned AppImage runtime.
- [ ] macOS `.app`/DMG payload/evidence reconciled with notices/licenses.
- [ ] No bundled/frozen third-party component is represented as Arvectum-authored source.
- [ ] License obligations for intended commercial distribution are satisfied.

## Chain of title for ООО «Арвектум»

Review actual documents; Git authorship alone is not chain-of-title evidence. Legal checklist references: ГК РФ arts. 1228, 1234, 1295, 1296, 1297. Classify each contribution by the actual legal basis rather than applying a generic assignment assumption.

- [ ] Every material human author/contributor is identified or otherwise accounted for in the legal evidence set.
- [ ] Founder/pre-company contributions have a documented rights basis for ООО «Арвектум» where required.
- [ ] Employee IP clauses, job duties and service-work facts are reviewed where applicable.
- [ ] Contractor/freelancer agreements and assignments/licenses are reviewed where applicable.
- [ ] Commissioned works are classified under the correct contractual/IP regime rather than assumed to belong to the customer automatically.
- [ ] Rights to commissioned visual/brand assets are documented.
- [ ] Known third-party and AI-assisted inputs are consistent with company IP policy.
- [ ] No unresolved ownership dispute or incompatible source license remains.

### Legal evidence

Confidential originals may stay outside the public repository. Record a stable internal reference, date, scope and reviewer instead of exposing personal/confidential documents.

| Evidence/document reference | Date | Scope | Verified by |
|---|---|---|---|
|  |  |  |  |

## Decision

Select exactly one:

- [ ] **APPROVED** — human source review, artifact/license reconciliation and chain-of-title review are complete; no blocker remains.
- [ ] **CONDITIONAL** — remediation below is mandatory before tagging.
- [ ] **HOLD** — unresolved provenance/license/ownership issue blocks release.

Remediation: _____________________________________________________

A clean IP tag may be created only after **APPROVED** and must point to the exact reviewed candidate commit `7c3bdbd005e6ff27db8f5a00071dc81c8595dd9b`. Any source/remediation change after review requires selecting and reviewing a new candidate.

Suggested convention: `ip-clean/0.2.3/<YYYY-MM-DD>`.

Approval/signature reference: _____________________________________
