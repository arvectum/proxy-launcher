# APL-IP-001 — human/legal sign-off record

Status: **PENDING AUTHORIZED HUMAN/LEGAL REVIEW**. This record must be completed before a clean IP baseline/tag is created.

## Candidate identity

- Product version: ____________________
- Candidate commit SHA: ________________________________________
- Source provenance manifest SHA-256: ___________________________
- Final SBOM SHA-256: ___________________________________________
- `THIRD_PARTY_NOTICES.txt` SHA-256: _____________________________
- Reviewer / authority: _________________________________________
- Review date: __________________________________________________

## Significant-source review

Inspect the candidate tree, relevant Git history and all provenance-manifest review findings.

- [ ] Core/control plane and configuration/state ownership.
- [ ] Windows backend/recovery/diagnostics/release integration.
- [ ] Linux/Astra backend, NetworkManager/PolicyKit, recovery, diagnostics, autostart and packaging glue.
- [ ] macOS backend, `networksetup` preflight, recovery, diagnostics, LaunchAgent and packaging glue.
- [ ] Routing control plane: `routing_rules.py`, `windows_app_routing.py`, `routing_ownership.py`.
- [ ] GUI/failure-state logic and security/privacy boundaries.
- [ ] Build/release/CI scripts that materially affect shipped artifacts or provenance.
- [ ] Visual/brand assets claimed by ООО «Арвектум».
- [ ] Any material AI-assisted or imported/template-like fragments have been reviewed and deliberately accepted, rewritten, or separately licensed as appropriate.

Do not delete/rewrite Git history to manufacture provenance or authorship.

### Findings

| Path/module | Finding/source | Review action | Final disposition |
|---|---|---|---|
|  |  |  |  |

## Artifact / third-party reconciliation

- [ ] Windows portable SBOM reconciled with notices/licenses.
- [ ] Windows installer SBOM reconciled with notices/licenses.
- [ ] Linux `.deb` SBOM reconciled with notices/licenses.
- [ ] Linux AppImage SBOM reconciled with notices/licenses, including the pinned AppImage runtime.
- [ ] macOS `.app`/DMG SBOM reconciled with notices/licenses.
- [ ] No bundled/frozen third-party component is represented as Arvectum-authored source.
- [ ] License obligations for intended commercial distribution are satisfied.

## Chain of title for ООО «Арвектум»

Review actual documents; Git authorship alone is not chain-of-title evidence.

- [ ] Employee IP clauses/assignments reviewed where applicable.
- [ ] Contractor/freelancer agreements and assignments reviewed where applicable.
- [ ] Material pre-company contributions have an explicit transfer/license into ООО «Арвектум» where required.
- [ ] Rights to commissioned visual/brand assets are documented.
- [ ] Known third-party and AI-assisted inputs are consistent with company IP policy.
- [ ] No unresolved ownership dispute or incompatible source license remains.

### Legal evidence

| Evidence/document | Date | Scope | Verified by |
|---|---|---|---|
|  |  |  |  |

## Decision

Select exactly one:

- [ ] **APPROVED** — human source review, artifact/license reconciliation and chain-of-title review are complete; no blocker remains.
- [ ] **CONDITIONAL** — remediation below is mandatory before tagging.
- [ ] **HOLD** — unresolved provenance/license/ownership issue blocks release.

Remediation: _____________________________________________________

A clean IP tag may be created only after **APPROVED** and must point to the exact reviewed commit. Suggested convention: `ip-clean/<product-version>/<YYYY-MM-DD>`.

Approval/signature reference: _____________________________________
