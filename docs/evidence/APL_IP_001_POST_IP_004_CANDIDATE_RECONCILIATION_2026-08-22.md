# APL-IP-001 — post-APL-IP-004 exact candidate / evidence reconciliation

Status: **ENGINEERING RECONCILIATION COMPLETE / HUMAN-LEGAL APPROVAL STILL REQUIRED**  
Date: 2026-08-22

This record closes the repository/Web reconciliation step required after APL-IP-004. It does not grant legal approval, does not execute an author -> ООО «Арвектум» rights transfer, and does not authorize a clean-IP tag.

## 1. Exact candidate selection

The immutable APL-IP-003/post-refactor source-review anchor remains:

- commit: `8ad54018e6d6251c906a06d09fd464c8931c14b2`;
- tree: `eac5db739e7bd3fda595b09b2ec869ad06a87ba3`.

APL-IP-004 subsequently changed build/release/license-compliance source and therefore required a new exact clean-IP/commercial candidate. The selected post-APL-IP-004 candidate is:

- repository: `arvectum/proxy-launcher`;
- product version: `0.2.3`;
- candidate merge commit: `ef9846e151a2e4e7046169e0787603969018cc97` (merged PR #167);
- candidate tree: `98a09d821470a597715696e5ff3c7f376e5893a8`;
- validated PR head: `ab3f6aea8087ac09c3d8dcbdf348fcc7f6684f9f`;
- validated PR test-merge commit: `818a39591cd2377bd1c451294854d4f787a9f369`;
- PR head tree, PR test-merge tree and final merge-candidate tree: **identical** `98a09d821470a597715696e5ff3c7f376e5893a8`.

The final merge therefore has byte-for-byte the same file tree as the tree exercised by the PR #167 acceptance workflows. Merge topology differs; candidate contents do not.

## 2. Delta from the post-refactor source-review anchor

`8ad54018... -> ef9846e...` is 30 commits ahead with no history divergence.

The changed-file set is confined to governance/documentation, CI, packaging/release tooling, installer definition, third-party license material and APL-IP-004 tests. **None of the 45 product-source files in the post-refactor APL-IP-001 significant-source set changed.**

Consequences:

1. the bounded source/public-similarity review from `docs/evidence/APL_IP_001_POST_REFACTOR_REVIEW_2026-08-22.md` remains applicable to the unchanged product-source set;
2. no claim is made that old provenance/SBOM artifacts were generated for the new tree;
3. provenance was regenerated on the exact candidate-equivalent PR tree;
4. the build SBOM was regenerated and independently rebound to the candidate-equivalent tree;
5. APL-IP-004 package evidence is bound separately to the exact promoted-artifact lanes it changed.

## 3. Exact source-provenance evidence

Candidate-equivalent APL-IP-001 provenance workflow:

- workflow run: `32556717797`;
- workflow result: **SUCCESS**;
- artifact ID: `9471635320`;
- artifact name: `apl-ip-001-source-provenance`;
- artifact digest: `sha256:3a7d98c5b022545c9294e2ee264f55b1206fddc8f255dec6cb3b15b2ca045924`;
- `source-manifest.json` SHA-256: `baf27272def4c03c7f44852ff11aa1c2fdb32710f92ac0e322f94b557158a87b`;
- schema version: `2`;
- governed records: **377**;
- product-source records: **45**;
- automated provenance-marker findings: **0**;
- `human_review_required=true`;
- `legal_signoff_required=true`.

Manifest categories:

- documentation: 133;
- tests: 97;
- build/release: 62;
- product source: 45;
- CI: 29;
- governance/config: 11.

The increased governed-record count relative to the earlier post-refactor review is expected from the added APL-IP-001/APL-IP-004 governance, packaging and compliance files. It is not a product-source expansion.

## 4. Exact build-SBOM evidence

Candidate-equivalent SBOM workflow:

- workflow run: `32556717820`;
- workflow result: **SUCCESS**;
- artifact ID: `9471638388`;
- artifact digest: `sha256:f1927160a0be2852305b6abe37e0f03de61499cdfe19303b5595c3c063eaed91`;
- CycloneDX document SHA-256: `fccd5d2d94a4c2f8ebbc9fdde709db5b0fd1ae13f962f9046d706086a345ac4a`;
- CycloneDX spec: `1.6`.

The component set remains exactly the seven entries pinned by `requirements-build.lock.txt`:

- `altgraph 0.17.5`;
- `packaging 26.3`;
- `pefile 2024.8.26`;
- `pyinstaller 6.22.0`;
- `pyinstaller-hooks-contrib 2026.6`;
- `pywin32-ctypes 0.2.3`;
- `setuptools 84.0.0`.

The CycloneDX document hash remaining identical to the earlier post-refactor review is expected: APL-IP-004 did not change the frozen build lock. The new workflow run/artifact provides the required candidate-equivalent re-binding.

## 5. APL-IP-004 promoted-artifact evidence

APL-IP-004 is governed by `docs/APL_IP_004_THIRD_PARTY_LICENSE_BUNDLE_PROMOTED_ARTIFACT_COMPLIANCE.md`. Its common invariant is a generated, verified `THIRD_PARTY_LICENSES/manifest.json` plus complete discovered license/copyright texts from the exact build environment.

### Windows portable

- workflow run: `32556717827` — **SUCCESS**;
- explicit step `APL-IP-004 promoted portable license gate` — **SUCCESS**;
- artifact ID: `9471650858`;
- artifact digest: `sha256:7b4c2228267874fcc853bdd0a5fe8333b996ec513520df59fc6700540da4ccbf`;
- inner promoted portable ZIP SHA-256: `36269134a00216e547ea9c53a53bd3c89be29589194f458a17433f80784618af`;
- embedded `THIRD_PARTY_LICENSES/manifest.json` SHA-256: `f0e7e455d853493eb4ff35aa499a9233e30be92538f227d2a143918e81560fa9`;
- exact Windows bundle records Python, Tcl, Tk and PyInstaller license material and the promoted ZIP physically contains `LICENSE.txt`, `THIRD_PARTY_NOTICES.txt` and `THIRD_PARTY_LICENSES/`.

### Windows installer

- workflow run: `32556717718` — **SUCCESS after explicit rerun of the concurrency-cancelled job**;
- rerun job ID: `96999010497`;
- canonical portable baseline/license preparation: **SUCCESS**;
- current installer compile/metadata verification: **SUCCESS**;
- fresh / upgrade / repair / uninstall E2E: **SUCCESS**;
- Windows RC packaging and Gate R6 acceptance matrix: **SUCCESS**;
- artifact ID: `9472408987`;
- artifact name: `Arvectum-Proxy-Launcher-0.2.3-windows-x64-setup.exe`;
- artifact digest: `sha256:e384064dafca71d0d4f38d742ed6a68d947b428c28677b611c18316fcf72cc3e`.

The original scheduled final PR-head job was cancelled by workflow concurrency before checkout completed; the preserved workflow run was deliberately re-run during this reconciliation. The rerun exercised the same PR #167 candidate-equivalent tree and completed the installer acceptance contract rather than inferring compliance from source inspection.

### Debian `.deb`

- workflow run: `32556717706` — **SUCCESS** on Ubuntu 22.04 and 24.04;
- Ubuntu 22.04 artifact ID `9471643586`, digest `sha256:d6c441827a7129b7389d9efc5b5f08a0d9c27929a908d214408a80e33068d14e`;
- Ubuntu 24.04 artifact ID `9471642930`, digest `sha256:d1e2424de968f65f2c596d9ceafa721678c52c6762e174950b9f47289897b21e`;
- logs record bundle build and verification before package creation and show `THIRD_PARTY_LICENSES/manifest.json` plus bundled license texts in `/usr/share/doc/arvectum-proxy-launcher/`.

### macOS `.app` / DMG

- workflow run: `32556717755` — **SUCCESS** on Apple Silicon and Intel runners;
- Apple Silicon artifact ID `9471642464`, digest `sha256:caff279f3dc65f1cbfa7be31e3ecfee48a4ae0c9098bf147a1263d82e05cb923`;
- Intel artifact ID `9471655708`, digest `sha256:b861afeaad798111764fc6e7bc9a1c87ec5cfe22407c887fdb77412d21e2d241`;
- logs record bundle generation/verification inside `.app`, verification before DMG creation, and successful DMG integrity/mount inspection.

### AppImage

AppImage remains **EXCLUDED / HOLD**. APL-IP-004 carries the common desktop bundle into the AppImage path but does not resolve the pinned type-2 runtime/transitive obligations identified by Finding L-2, including the applicable libfuse/LGPL path.

## 6. L-1 disposition

Finding L-1 is **ENGINEERING-REMEDIATED** for newly built promoted artifacts in all four selected desktop lanes:

- Windows portable;
- Windows installer;
- Debian `.deb`;
- macOS `.app` / DMG.

This disposition does **not** mean legal/commercial `APPROVED`. It means the specific engineering gap identified by L-1 — absence of a complete, verified third-party license-text bundle in promoted frozen artifacts — has been remediated and evidenced.

Historical artifacts are not retroactively relabeled.

## 7. Findings after reconciliation

| ID | Finding | Post-reconciliation status |
|---|---|---|
| R-1 | Executed author -> ООО «Арвектум» rights basis | **PENDING / HUMAN** |
| R-2 | Rospatent registration/transfer factual status | **PENDING / HUMAN** |
| R-3 | Corporate/interested-transaction basis where applicable | **PENDING / HUMAN** |
| L-1 | Complete third-party license/notice bundle for promoted artifacts | **ENGINEERING-REMEDIATED**; no legal approval implied |
| L-2 | AppImage downstream/type-2-runtime compliance | **EXCLUDED / HOLD** |

The human factual provenance carry-forward also still requires authorized confirmation for the selected post-APL-IP-004 candidate before final approval.

## 8. Decision boundary

Repository/Web reconciliation result: **PASS FOR ENGINEERING EVIDENCE BINDING / CONDITIONAL OVERALL**.

The next action is not another automated source refactor. The remaining release-blocking APL-IP-001 work is the authorized human/legal layer: R-1, R-2, R-3, factual confirmation and final sign-off.

A clean-IP tag remains prohibited until the canonical sign-off explicitly records `APPROVED`. If any product source, build dependency, packaging/compliance implementation or selected promoted-artifact contents change after candidate `ef9846e...`, a new exact candidate/evidence reconciliation is required before tagging.
