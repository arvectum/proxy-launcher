# APL-IP-001 — exact review-candidate evidence binding

Status: **CANDIDATE BOUND / HUMAN-LEGAL APPROVAL PENDING**

This record binds the automated APL-IP-001 evidence to one exact source candidate. It does not approve authorship, chain of title, third-party license compliance or a clean-IP tag.

## Candidate identity

- Product: Arvectum Proxy Launcher
- Version: `0.2.3`
- Review candidate commit (`main`): `7c3bdbd005e6ff27db8f5a00071dc81c8595dd9b`
- Review candidate source tree: `9c372b440919b3b9e69d78ab0a85dca3f387d5af`
- Candidate merge commit verification: GitHub-verified signature
- Candidate purpose: bounded APL-IP-001 human authorship/provenance and chain-of-title review

The clean IP tag, if eventually authorized, must point to this exact candidate commit unless remediation changes source; in that case a new candidate must be selected and reviewed.

## CI tree-equivalence proof

PR #113 was tested using the GitHub pull-request merge ref and its branch head before squash merge.

- PR head: `b55b02b1fba3fed14ff6fea3df4cb3e9a05e3a8b`
- PR test merge ref: `56d4d83dd075cd23ba5db4fa7497aecf45bb59d6`
- final `main` review candidate: `7c3bdbd005e6ff27db8f5a00071dc81c8595dd9b`
- tree SHA for all three: `9c372b440919b3b9e69d78ab0a85dca3f387d5af`

Therefore the tested provenance/SBOM inputs are byte-for-byte the same repository tree as the selected review candidate, even though the commit IDs differ because GitHub created a PR merge ref and then a squash commit.

## Provenance evidence

- Workflow: `APL-IP-001 provenance`
- Workflow run: `32409782542`
- Workflow result: `SUCCESS`
- Artifact name: `apl-ip-001-source-provenance`
- Artifact ID: `9421664020`
- Artifact ZIP SHA-256/digest: `528990e85b79a441ad8477451cf0537e47d6f3b5398056d4672d476690407b42`
- Manifest file: `source-manifest.json`
- Manifest SHA-256: `7b1f42a124c1b0cf068937bb3bb8554609ab7294eb68583ba577b7ead93f1927`
- Manifest schema: `2`
- Governed records: `315`
- Product-source records: `34`
- Automated provenance findings: `0`
- `human_review_required`: `true`
- `legal_signoff_required`: `true`
- Marker detection: `header-oriented provenance/license markers`

Zero automated findings means only that this automated marker class found no unresolved signal. It is not proof of human authorship or ownership.

## Build SBOM evidence

- Workflow: `SBOM`
- Workflow run: `32409782544`
- Workflow result: `SUCCESS`
- Artifact ID: `9421675129`
- Artifact ZIP SHA-256/digest: `5831c5bec8d0139a48e3cd55e23bfb90d884a0b95abefd92e2ce718e20fa287d`
- SBOM: `arvectum-proxy-launcher-build.cdx.json`
- SBOM SHA-256: `fccd5d2d94a4c2f8ebbc9fdde709db5b0fd1ae13f962f9046d706086a345ac4a`
- Format: CycloneDX `1.6`
- Component count: `7`

This is a **build-dependency SBOM**, not a universal inventory of every shipped Windows/Linux/macOS payload. Platform artifact reconciliation remains a mandatory human/legal review item.

## Third-party notice identity

- `THIRD_PARTY_NOTICES.txt` SHA-256: `c36fab57e42132ebcc4201d681e706dbd6fad3c54630d887aa836d04bd192530`

The notice separates potentially redistributed runtime components, build-only tools and operating-system dependencies. Human review must reconcile it with the actual platform payload evidence.

## Relationship to sealed Windows 0.2.3 release

Canonical Windows production signing evidence identifies:

- artifact build commit: `54ce2585222948b51c67510ea620516ea6c3f876`
- release policy commit: `47823585c42da54ab51dc2246583dc24d74d4ba6`
- tag: `v0.2.3-ru.2`
- portable ZIP SHA-256: `62d313547b4d8c2c8e6951d6cd866bb954fdf199ad7650063c8ed3bfbc455801`
- installer SHA-256: `5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414`

A repository compare from the artifact build commit to the review candidate shows **no changes to the 34 top-level product-source files**. The intervening changes are governance/documentation/tests/CI/build-release and Windows acceptance/signing tooling. This allows the human review to relate the candidate's product runtime source to the already sealed Windows 0.2.3 artifact while still reviewing the newer build/release/governance tooling as part of the candidate tree.

This statement does not substitute for platform payload/license reconciliation.

## Required human/legal completion

Use:

- `docs/APL_IP_001_REVIEW_PACKET.md`
- `docs/APL_IP_001_HUMAN_LEGAL_SIGNOFF.md`

The authorized reviewer must still:

1. review the 34-file significant-source set plus material build/release scripts and relevant history;
2. identify and disposition any AI-assisted/imported/template-like material;
3. reconcile the build SBOM and platform payload evidence with `THIRD_PARTY_NOTICES.txt` and license obligations;
4. review the actual chain-of-title evidence for ООО «Арвектум» (founder/pre-company, employee, contractor/freelancer and commissioned visual/brand contributions as applicable);
5. select exactly one decision: `APPROVED`, `CONDITIONAL`, or `HOLD`.

No automation may select `APPROVED` on behalf of the authorized reviewer. No `ip-clean/...` tag may be created until the sign-off is `APPROVED`.
