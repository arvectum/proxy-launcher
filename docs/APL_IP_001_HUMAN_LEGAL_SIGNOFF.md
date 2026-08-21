# APL-IP-001 — human/legal sign-off record

Status: **HUMAN SOURCE/PROVENANCE CONFIRMED / RIGHTS INSTRUMENT + FINAL LEGAL RECONCILIATION PENDING**. A clean IP baseline/tag must not be created yet.

Use `docs/APL_IP_001_REVIEW_PACKET.md` as the bounded review guide, `docs/evidence/APL_IP_001_REVIEW_CANDIDATE_2026-08-20.md` as the automated evidence binding, and `docs/evidence/APL_IP_001_HUMAN_FACT_CONFIRMATION_2026-08-21.md` as the human factual confirmation. Do not treat CI, hashes, Git authorship, commit metadata or AI tooling as legal proof of authorship or ownership by themselves.

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
- Factual human reviewer / authority: project owner/author
- Human fact-confirmation date: `2026-08-21`
- Final legal reviewer / authority: __________________________________
- Final legal review date: ________________________________________

Automated candidate facts: manifest schema `2`; `315` governed records; `34` product-source records; `0` automated provenance findings; `human_review_required=true`; `legal_signoff_required=true`. The PR head, PR merge-test ref and candidate commit share the same source tree SHA, as recorded in the candidate evidence file.

## Significant-source review

The repository pre-review covered all 34 significant product-source files and 75 material build/release files. Human factual confirmation additionally established that the material core/recovery/routing/platform architecture was consciously reviewed/adopted by the human developer, deliberate copying from external projects was not used, and AI-assisted code was human-reviewed and accepted/corrected before inclusion.

- [x] Core/control plane and configuration/state ownership — human architecture confirmation recorded.
- [x] Windows backend/recovery/diagnostics integration — human platform confirmation recorded.
- [x] Linux/Astra backend, NetworkManager/PolicyKit, recovery, diagnostics and autostart — human platform confirmation recorded.
- [x] macOS backend, `networksetup` preflight, recovery, diagnostics and LaunchAgent — human platform confirmation recorded.
- [x] Routing control plane: `routing_rules.py`, `windows_app_routing.py`, `routing_ownership.py` — human architecture confirmation recorded.
- [ ] GUI/failure-state logic and security/privacy boundaries — repository pre-review complete; retain for final reviewer confirmation.
- [ ] Build/release/CI scripts that materially affect shipped artifacts or provenance — repository pre-review complete; retain for final reviewer confirmation.
- [x] Base visual/brand asset — project owner/author confirmed personal creation of the base Arvectum logo/monogram; no external designer for that asset.
- [x] Every automated provenance finding is investigated and dispositioned — candidate automated count `0`; prior two false positives are documented and scanner regression-tested.
- [x] Material AI-assisted/imported/template-like source — project owner/author confirmed AI-generated code was reviewed and accepted and/or corrected; deliberate external-project copying was not used.
- [x] Human creative contribution is identifiable for material product modules; AI/tool identities are not represented as legal authors.

Do not delete/rewrite Git history to manufacture provenance or authorship.

### Findings

| Path/module | Finding/source | Review action | Final disposition |
|---|---|---|---|
| Significant source set | Git contributor identities | Human mapping confirmed all `arvectum`/`arutyunoveth` identities belong to the same human developer; OpenAI is AI/tool identity; GitHub Actions is automation | SOURCE CONTRIBUTOR IDENTITY RESOLVED |
| Base Arvectum logo/monogram | Human question | Project owner/author confirmed personal creation | EXTERNAL DESIGNER RISK NOT IDENTIFIED |
| Material source | AI/external-origin question | Human confirmed no deliberate copying from Stack Overflow/GitHub/other projects and human review/correction of AI-generated code | FACTUAL PROVENANCE CONFIRMED; LEGAL RIGHTS DOCUMENT STILL REQUIRED |

## Artifact / third-party reconciliation

The repository CI SBOM is a build-dependency SBOM. Platform payload evidence must be reviewed separately; do not use one build SBOM as a universal shipped-artifact inventory.

- [ ] Build SBOM reconciled with `requirements-build.lock.txt` — automated/preliminary reconciliation exists; final reviewer confirmation pending.
- [ ] Windows portable payload/evidence reconciled with notices/licenses.
- [ ] Windows installer payload/evidence reconciled with notices/licenses.
- [ ] Linux `.deb` payload/evidence reconciled with notices/licenses.
- [ ] Linux AppImage payload/evidence reconciled with notices/licenses, including the pinned AppImage runtime.
- [ ] macOS `.app`/DMG payload/evidence reconciled with notices/licenses.
- [ ] No bundled/frozen third-party component is represented as Arvectum-authored source — pre-review found no contrary signal; final reviewer confirmation pending.
- [ ] License obligations for intended commercial distribution are satisfied.

## Chain of title for ООО «Арвектум»

Review actual documents; Git authorship alone is not chain-of-title evidence. Legal checklist references: ГК РФ arts. 1228, 1234, 1295, 1296, 1297. Classify each contribution by the actual legal basis rather than applying a generic assignment assumption.

- [x] Every material human source contributor identified by repository pre-review is accounted for: the `arvectum`/`arutyunoveth` Git identities map to one human developer/project owner; OpenAI and GitHub Actions are non-human tool/automation identities.
- [ ] Author → ООО «Арвектум» rights basis is documented by an executed written instrument or independently verified service-work basis.
- [ ] Founder/pre-company contributions, if any outside the candidate source history, have a documented rights basis for ООО «Арвектум» where required.
- [ ] Employee IP clauses, job duties and service-work facts are reviewed where applicable.
- [x] No separate contractor/freelancer source contributor was identified in the significant-source Git history.
- [ ] Commissioned works/other visual assets, if any beyond the self-authored base logo, are classified under the correct contractual/IP regime.
- [x] Base Arvectum logo/monogram provenance is human-confirmed as self-authored; company rights basis remains covered by the same author→company documentation requirement.
- [ ] Known third-party and AI-assisted inputs are consistent with company IP policy — factual AI review confirmed; final license/legal reconciliation pending.
- [ ] No unresolved ownership dispute or incompatible source license remains.

### Legal evidence

Confidential originals may stay outside the public repository. Record a stable internal reference, date, scope and reviewer instead of exposing personal/confidential documents.

| Evidence/document reference | Date | Scope | Verified by |
|---|---|---|---|
| `docs/evidence/APL_IP_001_HUMAN_FACT_CONFIRMATION_2026-08-21.md` | 2026-08-21 | Contributor identity mapping; human creative control; external-copying/AI facts; base logo authorship | project owner/author |
| `docs/legal/APL_IP_001_RIGHTS_ASSIGNMENT_TEMPLATE.md` | draft | Author→ООО written rights-instrument template; **not executed** | pending legal execution |

## Decision

Select exactly one only after the remaining legal/documentary gates are complete:

- [ ] **APPROVED** — human source review, artifact/license reconciliation and chain-of-title review are complete; no blocker remains.
- [ ] **CONDITIONAL** — remediation below is mandatory before tagging.
- [ ] **HOLD** — unresolved provenance/license/ownership issue blocks release.

Current blocking items:

1. execute/retain an appropriate written author→ООО «Арвектум» rights instrument (or establish an equally strong documented existing rights basis);
2. complete final platform payload/license reconciliation and legal/compliance confirmation;
3. close the two retained human-review scopes for GUI/failure-state and material build/release/CI scripts if the final reviewer requires separate confirmation.

A clean IP tag may be created only after **APPROVED** and must point to the exact reviewed candidate commit `7c3bdbd005e6ff27db8f5a00071dc81c8595dd9b`. Any source/remediation change after review requires selecting and reviewing a new candidate.

Suggested convention: `ip-clean/0.2.3/<YYYY-MM-DD>`.

Approval/signature reference: _____________________________________
