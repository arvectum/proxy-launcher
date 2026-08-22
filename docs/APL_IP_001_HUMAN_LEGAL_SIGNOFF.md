# APL-IP-001 — human/legal sign-off record

> **HISTORICAL PRE-REFACTOR RECORD.** This file preserves the pre-refactor review/carry-forward evidence and must not be used as the current approval form. The canonical post-refactor decision record is `docs/APL_IP_001_POST_REFACTOR_SIGNOFF.md`; the current review evidence is `docs/evidence/APL_IP_001_POST_REFACTOR_REVIEW_2026-08-22.md`.

Status: **AUTONOMOUS CARRY-FORWARD CLOSURE COMPLETE / HUMAN-LEGAL RIGHTS EXECUTION PENDING / FINAL CLEAN-IP REVIEW DEFERRED POST-REFACTOR**. A pre-refactor clean-IP baseline/tag must not be created.

Use `docs/APL_IP_001_REVIEW_PACKET.md` as the bounded historical review guide, `docs/evidence/APL_IP_001_REVIEW_CANDIDATE_2026-08-20.md` as the historical automated evidence binding, `docs/evidence/APL_IP_001_HUMAN_FACT_CONFIRMATION_2026-08-21.md` as the human factual confirmation, `docs/evidence/APL_IP_001_PLATFORM_LICENSE_RECONCILIATION_2026-08-21.md` as the platform/license carry-forward reconciliation, and `docs/evidence/APL_IP_001_CARRY_FORWARD_CLOSURE_2026-08-21.md` as the closure record. Do not treat CI, hashes, Git authorship, commit metadata or AI tooling as legal proof of authorship or ownership by themselves.

## Candidate identity

- Product version: `0.2.3`
- Historical review candidate commit SHA: `7c3bdbd005e6ff27db8f5a00071dc81c8595dd9b`
- Historical candidate source tree SHA: `9c372b440919b3b9e69d78ab0a85dca3f387d5af`
- Source provenance artifact/run reference: workflow run `32409782542`, artifact `9421664020`
- Source provenance manifest SHA-256: `7b1f42a124c1b0cf068937bb3bb8554609ab7294eb68583ba577b7ead93f1927`
- Source provenance artifact digest: `528990e85b79a441ad8477451cf0537e47d6f3b5398056d4672d476690407b42`
- Build SBOM artifact/run reference: workflow run `32409782544`, artifact `9421675129`
- Build SBOM SHA-256: `fccd5d2d94a4c2f8ebbc9fdde709db5b0fd1ae13f962f9046d706086a345ac4a`
- Platform payload/release-evidence references: Windows `docs/evidence/WINDOWS_RUSSIAN_PRODUCTION_SIGNING_ACCEPTANCE_2026-08-20.json`; cross-platform carry-forward `docs/evidence/APL_IP_001_PLATFORM_LICENSE_RECONCILIATION_2026-08-21.md`
- Factual human reviewer / authority: project owner/author
- Human fact-confirmation date: `2026-08-21`
- Final post-refactor legal reviewer / authority: __________________________________
- Final post-refactor legal review date: ________________________________________

Automated historical-candidate facts: manifest schema `2`; `315` governed records; `34` product-source records; `0` automated provenance findings; `human_review_required=true`; `legal_signoff_required=true`. The PR head, PR merge-test ref and candidate commit share the same source tree SHA, as recorded in the candidate evidence file.

The carry-forward packaging hardening intentionally post-dates this historical candidate. It must survive APL-IP-003 and be reviewed in the new post-refactor candidate; it is not retroactively attributed to `7c3bdbd...`.

## Significant-source review

The repository pre-review covered all 34 significant product-source files and 75 material build/release files. Human factual confirmation additionally established that the material core/recovery/routing/platform architecture was consciously reviewed/adopted by the human developer, deliberate copying from external projects was not used, and AI-assisted code was human-reviewed and accepted/corrected before inclusion.

- [x] Core/control plane and configuration/state ownership — human architecture confirmation recorded.
- [x] Windows backend/recovery/diagnostics integration — human platform confirmation recorded.
- [x] Linux/Astra backend, NetworkManager/PolicyKit, recovery, diagnostics and autostart — human platform confirmation recorded.
- [x] macOS backend, `networksetup` preflight, recovery, diagnostics and LaunchAgent — human platform confirmation recorded.
- [x] Routing control plane: `routing_rules.py`, `windows_app_routing.py`, `routing_ownership.py` — human architecture confirmation recorded.
- [x] GUI/failure-state logic and security/privacy boundaries — repository pre-review completed and no automated provenance finding remained; final clean-IP review will be repeated against the post-refactor candidate rather than falsely approving the historical tree.
- [x] Build/release/CI scripts that materially affect shipped artifacts or provenance — repository pre-review completed; carry-forward packaging boundaries are now explicitly hardened/tested and will be re-reviewed post-refactor.
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
| Material source | AI/external-origin question | Human confirmed no deliberate copying from Stack Overflow/GitHub/other projects and human review/correction of AI-generated code | FACTUAL PROVENANCE CONFIRMED; COMPANY RIGHTS EXECUTION STILL REQUIRED |

## Artifact / third-party reconciliation

The repository CI SBOM is a build-dependency SBOM, not a universal final-artifact inventory. The carry-forward closure records each platform boundary separately in `docs/evidence/APL_IP_001_PLATFORM_LICENSE_RECONCILIATION_2026-08-21.md`.

- [x] Build SBOM reconciled with `requirements-build.lock.txt` — CI generates CycloneDX 1.6 from the exact lock and fails on missing/mismatched locked components.
- [x] Windows portable release-set evidence reconciled with notices/licenses — exact Russian-first release ceremony stages `LICENSE.txt` and `THIRD_PARTY_NOTICES.txt` beside the hash-bound artifact.
- [x] Windows installer release-set evidence reconciled with notices/licenses — same exact governed release-set boundary; Inno Setup remains build tooling rather than Arvectum-authored source.
- [x] Linux `.deb` package contract reconciled with notices/licenses — package installs product license and third-party notices under `/usr/share/doc/arvectum-proxy-launcher`; `network-manager` stays a system dependency.
- [x] Linux AppImage package contract now carries product/license notices and keeps the runtime exact SHA-256 pin.
- [ ] Linux AppImage **commercial-distribution legal clearance** — bounded hold: the exact type-2 runtime license identifies statically linked `musl`, `libfuse`, `squashfuse`, `libzstd` and `zlib`; exact downstream notice/source/relink obligations must be confirmed before production AppImage promotion. AppImage is optional and `.deb` remains preferred.
- [x] macOS `.app`/DMG package contracts now carry `LICENSE.txt` and `THIRD_PARTY_NOTICES.txt`; exact new artifact-byte evidence is intentionally deferred to the post-refactor build/candidate.
- [x] No bundled/frozen third-party component is represented as Arvectum-authored source in the reviewed inventory/notices.
- [ ] Final legal confirmation that all obligations for every promoted commercial distribution artifact are satisfied — reserved for the authorized post-refactor review; no engineering record may self-approve this legal conclusion.

## Chain of title for ООО «Арвектум»

Review actual documents; Git authorship alone is not chain-of-title evidence. Legal checklist references: ГК РФ arts. 1228, 1234, 1295, 1296, 1297. Classify each contribution by the actual legal basis rather than applying a generic assignment assumption.

- [x] Every material human source contributor identified by repository pre-review is accounted for: the `arvectum`/`arutyunoveth` Git identities map to one human developer/project owner; OpenAI and GitHub Actions are non-human tool/automation identities.
- [ ] Author → ООО «Арвектум» rights basis is documented by an executed written instrument or independently verified service-work basis.
- [ ] Founder/pre-company contributions, if any outside the candidate source history, have a documented rights basis for ООО «Арвектум» where required.
- [ ] Employee IP clauses, job duties and service-work facts are reviewed where applicable.
- [x] No separate contractor/freelancer source contributor was identified in the significant-source Git history.
- [ ] Commissioned works/other visual assets, if any beyond the self-authored base logo, are classified under the correct contractual/IP regime.
- [x] Base Arvectum logo/monogram provenance is human-confirmed as self-authored; company rights basis remains covered by the same author→company documentation requirement.
- [x] Known AI-assisted inputs are factually accounted for without representing AI/tool identities as legal authors; third-party distribution obligations are separately bounded above.
- [ ] No unresolved ownership dispute or incompatible distribution license remains in the final promoted post-refactor artifact set — final legal decision pending.

### Legal evidence

Confidential originals may stay outside the public repository. Record a stable internal reference, date, scope and reviewer instead of exposing personal/confidential documents.

| Evidence/document reference | Date | Scope | Verified by |
|---|---|---|---|
| `docs/evidence/APL_IP_001_HUMAN_FACT_CONFIRMATION_2026-08-21.md` | 2026-08-21 | Contributor identity mapping; human creative control; external-copying/AI facts; base logo authorship | project owner/author |
| `docs/evidence/APL_IP_001_PLATFORM_LICENSE_RECONCILIATION_2026-08-21.md` | 2026-08-21 | Repository/build/package-level platform-license carry-forward boundaries | engineering evidence |
| `docs/evidence/APL_IP_001_CARRY_FORWARD_CLOSURE_2026-08-21.md` | 2026-08-21 | Autonomous carry-forward closure and explicit remaining human/legal boundary | engineering evidence |
| `docs/legal/APL_IP_001_RIGHTS_ASSIGNMENT_TEMPLATE.md` | draft | Author→ООО written rights-instrument template; **not executed** | pending human/legal execution |
| Executed rights-basis evidence reference | __________________ | Author→ООО chain of title | __________________ |

## Carry-forward decision

- [x] **AUTONOMOUS CARRY-FORWARD CLOSED** — repository/provenance/package-control work required before the canonical refactor is complete; remaining pre-refactor action requires an authorized human/legal act.
- [ ] **RIGHTS EXECUTED** — an executed author→ООО rights-basis reference has been recorded above.

The historical candidate is not being given a clean-IP legal verdict because APL-IP-003 is deliberately next. The final clean-IP decision is reserved for the new post-refactor exact candidate:

- [ ] **APPROVED** — post-refactor human source review, exact promoted-artifact/license reconciliation and chain-of-title review complete; no blocker remains.
- [ ] **CONDITIONAL** — post-refactor remediation mandatory before tagging.
- [ ] **HOLD** — unresolved provenance/license/ownership issue blocks release.

Current human/legal item before APL-IP-003:

1. execute/retain the appropriate written author→ООО «Арвектум» rights instrument (or establish an equally strong documented existing rights basis) and record a stable non-secret evidence reference.

Post-refactor items are deliberately not treated as unfinished pre-refactor engineering: select a new exact candidate, regenerate provenance/SBOM evidence, rebuild/reconcile the promoted platform artifacts, make the authorized legal/commercial-distribution decision, and only then create a clean-IP tag.

A pre-refactor clean-IP tag must **not** be created. The old suggested `ip-clean/0.2.3/<YYYY-MM-DD>` convention is superseded for this historical candidate; tag naming will be selected for the new post-refactor APPROVED candidate.

Approval/signature reference: _____________________________________
