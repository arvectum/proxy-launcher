# APL-IP-001 — post-refactor IP / provenance / distribution review

Status: **AUTONOMOUS POST-REFACTOR REVIEW COMPLETE / CONDITIONAL — AUTHORIZED HUMAN-LEGAL EXECUTION REQUIRED**

Date: 2026-08-22

This record binds the completed APL-IP-003 engineering refactor to the post-refactor APL-IP-001 review. It is an evidence-driven engineering/compliance review, not a legal opinion, not a signature, and not a substitute for an authorized human/legal decision.

## 1. Exact review candidate

- Repository: `arvectum/proxy-launcher`
- Product version: `0.2.3`
- Protected-`main` post-refactor candidate: `8ad54018e6d6251c906a06d09fd464c8931c14b2`
- Candidate tree: `eac5db739e7bd3fda595b09b2ec869ad06a87ba3`
- Candidate PR head: `1625e44ad1d3d96a5f7218545c74ffb1d85de93f`
- PR head -> candidate compare: one merge-topology commit, **zero changed files**; therefore the reviewed candidate file tree is byte-for-byte identical to the fully validated PR tree.

APL-IP-003 engineering completion is recorded in `docs/evidence/APL_IP_003_ENGINEERING_COMPLETION.md`.

## 2. Exact source-provenance evidence

Candidate-bound APL-IP-001 provenance workflow:

- workflow run: `32552042186`
- artifact ID: `9470327809`
- artifact name: `apl-ip-001-source-provenance`
- artifact digest: `sha256:36c9a9e267d38b1241d1e8afd17096bd7ce072c9665f56a38584054555c752bd`
- `source-manifest.json` SHA-256: `5e33393b0864a7804d4303ee2d5bf64daea36a69f5a40e2c3741d3ed3172815d`
- schema: `2`
- governed records: **368**
- product-source records: **45**
- automated provenance-marker findings: **0**
- `human_review_required=true`
- `legal_signoff_required=true`

Category inventory:

- product source: 45
- tests: 96
- build/release: 60
- CI: 29
- documentation: 127
- governance/config: 11

A zero automated finding is not proof of authorship; it means this governed marker class produced no unresolved signal.

## 3. Current significant-source set

The post-refactor manifest contains 45 product-source files. This list supersedes the historical 34-file pre-refactor review list.

### Core / application / control / security

- `application_filesystem.py`
- `application_runtime.py`
- `backend_contract.py`
- `backend_runtime.py`
- `capability_model.py`
- `configuration_storage.py`
- `connection_test.py`
- `doctor.py`
- `local_proxy_transport.py`
- `logging_bridge.py`
- `portable_lifecycle.py`
- `process_supervision.py`
- `proxy_backend.py`
- `proxy_core.py`
- `proxy_gui.py`
- `recovery_autostart.py`
- `recovery_ownership.py`
- `recovery_state.py`
- `routing_ownership.py`
- `routing_policy.py`
- `routing_rules.py`
- `secret_redaction.py`
- `structured_logging.py`
- `system_proxy_runtime.py`

### Windows

- `windows_app_routing.py`
- `windows_backend.py`
- `windows_diagnostics.py`
- `windows_pac_recovery.py`
- `windows_single_instance.py`
- `windows_system_proxy.py`

### Linux / Astra

- `linux_autostart.py`
- `linux_backend.py`
- `linux_diagnostics.py`
- `linux_gui.py`
- `linux_networkmanager_preflight.py`
- `linux_policykit_ux.py`
- `linux_runtime.py`

### macOS

- `macos_autostart.py`
- `macos_backend.py`
- `macos_capability_ux.py`
- `macos_diagnostics.py`
- `macos_networksetup_preflight.py`
- `macos_runtime.py`

### QA helper source classified as product-source by manifest rules

- `qa/collect_macos_network_state.py`
- `qa/compare_macos_network_state.py`

## 4. Refactor lineage / provenance continuity

The historical review candidate was `7c3bdbd005e6ff27db8f5a00071dc81c8595dd9b`. The post-refactor candidate is 222 commits ahead of that candidate with no history divergence.

The refactor physically removed `proxy_core_legacy.py` (2515 lines deleted) and extracted explicit canonical owners including:

- `application_filesystem.py`
- `application_runtime.py`
- `configuration_storage.py`
- `local_proxy_transport.py`
- `logging_bridge.py`
- `portable_lifecycle.py`
- `process_supervision.py`
- `recovery_autostart.py`
- `routing_policy.py`
- `system_proxy_runtime.py`
- `windows_pac_recovery.py`
- `windows_system_proxy.py`

The bounded APL-IP-003 slice evidence records each extraction/refactor and its regression/package gates. This review found no indication that the additional canonical-owner files represent an imported external source tree; they are the documented product refactor/extraction lineage of the previously reviewed codebase.

Historical Git provenance was preserved. `.mailmap` normalizes the same human developer's historical identities without rewriting commits, while AI/tool and automation identities remain truthful and are not reassigned as human authors.

## 5. Human factual provenance carried forward

`docs/evidence/APL_IP_001_HUMAN_FACT_CONFIRMATION_2026-08-21.md` records the project owner's factual confirmation that:

- the `arvectum` / `arutyunoveth` identities belong to one human developer/project owner;
- OpenAI/tool and GitHub Actions identities are not human authors;
- material architecture/code was consciously reviewed and adopted by a human developer;
- no third-party code from Stack Overflow, GitHub or another external project was knowingly copied into the product;
- AI-assisted code was reviewed and accepted and/or corrected by the human developer before inclusion;
- the base Arvectum logo/monogram was personally created by the same project owner/author.

These facts remain provenance evidence. They do not themselves transfer exclusive rights to ООО «Арвектум».

## 6. Bounded public-similarity review

A bounded exact-phrase search was performed against public web/GitHub-indexed material using distinctive, high-information candidate-source phrases rather than generic Python idioms. Representative reviewed modules included:

- `proxy_core.py`
- `application_runtime.py`
- `configuration_storage.py`
- `secret_redaction.py`
- `recovery_state.py`
- `routing_rules.py`
- `windows_system_proxy.py`
- `windows_pac_recovery.py`
- `linux_backend.py`
- `macos_backend.py`

Representative exact project-specific phrases from composition, fail-closed WinINET ownership, PAC recovery, application orchestration, configuration persistence, recovery-state ownership and platform adapters produced **no identifiable external exact-source match**. Broader routing/platform queries produced unrelated keyword overlap only.

Disposition: **NO PUBLIC-SIMILARITY BLOCKER IDENTIFIED IN THE BOUNDED REVIEW**.

This result is not a mathematical proof that no similar code exists anywhere; it is a bounded review signal and must not be represented as a copyright certificate.

## 7. Exact build SBOM reconciliation

Candidate-bound SBOM workflow:

- workflow run: `32552042326`
- artifact ID: `9470330386`
- artifact digest: `sha256:8e24e7cb03ee22380672eaf9b6b6333485cadf099471378745c8503956c405af`
- CycloneDX document SHA-256: `fccd5d2d94a4c2f8ebbc9fdde709db5b0fd1ae13f962f9046d706086a345ac4a`
- CycloneDX spec: `1.6`

The SBOM contains exactly the seven components pinned by `requirements-build.lock.txt`:

- `altgraph 0.17.5`
- `packaging 26.3`
- `pefile 2024.8.26`
- `pyinstaller 6.22.0`
- `pyinstaller-hooks-contrib 2026.6`
- `pywin32-ctypes 0.2.3`
- `setuptools 84.0.0`

No unknown build dependency is introduced by the candidate SBOM.

The build SBOM is not by itself a complete final-artifact inventory; platform artifact obligations remain a separate release-boundary review.

## 8. Platform artifact evidence

Windows candidate-head evidence re-ran after the final completion contract:

- Windows full unit suite: **640 tests, OK**;
- sealed version: `0.2.3`;
- portable executable/package build: **SUCCESS**;
- Documents execution smoke: **SUCCESS**;
- packaged Doctor smoke: **SUCCESS**;
- installer fresh / upgrade / repair / uninstall E2E: **SUCCESS**;
- Gate R6 acceptance: **SUCCESS**.

The immediately preceding Slice 22 product tree completed a full 20/20 cross-platform matrix including macOS Apple Silicon/Intel `.app`/DMG, Debian package, AppImage, Debian/Ubuntu acceptance, controlled offline/no-index Windows build, provenance and security gates. Slice 23 added only the engineering-completion test/workflow contract and did not modify production/package source.

## 9. Third-party / distribution-license review

`THIRD_PARTY_NOTICES.txt` correctly distinguishes Arvectum source from Python/stdlib, Tcl/Tk, PyInstaller, AppImage runtime/build tooling and OS-provided components. The review nevertheless identified an important commercial-distribution compliance gap:

### Finding L-1 — promoted frozen artifacts need a full third-party license bundle

The current governed tree contains Arvectum's own `LICENSE` and `THIRD_PARTY_NOTICES.txt`, but no separate complete third-party license-text bundle for the runtime components that may be frozen into distributed desktop artifacts.

For promoted commercial artifacts, notices alone are not treated as sufficient evidence where an upstream license requires preservation/inclusion of its license or copyright notice. The release process must stage and verify the applicable complete license texts/notices for the exact shipped payload (including, when present, Python/PSF, Tcl/Tk and PyInstaller/bootloader obligations).

Disposition: **REMEDIATION REQUIRED BEFORE FINAL APPROVED COMMERCIAL ARTIFACT SET**.

### Finding L-2 — AppImage remains outside promoted commercial scope

`tools/appimage-toolchain.lock` pins AppImage type-2 runtime source commit `75849dce7cc37e4319b633df1f116ca895c71a12` and runtime SHA-256 `1cc49bcf1e2ccd593c379adb17c9f85a36d619088296504de95b1d06215aebbf`.

The exact upstream runtime license is MIT but explicitly identifies statically linked third-party code from musl libc, libfuse, squashfuse, libzstd and zlib. A promoted AppImage therefore requires a dedicated downstream compliance review/bundle, including the applicable LGPL obligations for the linked libfuse component.

Disposition: **APPIMAGE EXCLUDED FROM THE CLEAN-IP PROMOTED COMMERCIAL ARTIFACT SCOPE UNTIL SEPARATELY CLEARED**. The Debian `.deb` path remains the preferred Linux distribution path for this review.

## 10. Chain-of-title review for ООО «Арвектум»

Repository/Git evidence identifies one human developer/project owner behind the material human source identities and no separate contractor/freelancer source contributor in the significant-source history. AI/tool/automation identities are not treated as legal authors.

The remaining documentary chain-of-title gate is real and cannot be auto-approved:

### Finding R-1 — executed author -> ООО rights basis not recorded

The repository contains a draft rights instrument, but no executed written author -> ООО «Арвектум» evidence reference is recorded for the final post-refactor candidate.

Required action:

- execute/retain the appropriate written rights instrument or independently verify another valid existing rights basis;
- record a stable non-secret internal reference, date, scope and reviewer;
- do not publish confidential originals or personal data merely to satisfy repository governance.

The post-refactor execution-ready draft must bind candidate `8ad54018e6d6251c906a06d09fd464c8931c14b2`, tree `eac5db739e7bd3fda595b09b2ec869ad06a87ba3` and manifest SHA-256 `5e33393b0864a7804d4303ee2d5bf64daea36a69f5a40e2c3741d3ed3172815d`.

### Finding R-2 — Rospatent registration status must be confirmed

No repository evidence was found that establishes whether this exact computer program is already registered in Rospatent. Do not infer either status from silence.

Required authorized-review field:

- if **not registered**: record the factual status;
- if **registered**: record the certificate/registration reference and complete any legally required registration of the exclusive-right transfer.

### Finding R-3 — corporate/interested-transaction basis must be recorded where applicable

If the individual author is also the company's director, controlling participant or otherwise an interested person in the author -> ООО transaction, the corporate approval/exception basis under the company's actual participant/management structure and charter must be checked and recorded. Do not assume a sole-participant exception unless it is factually true for the company at execution time.

## 11. Review verdict

### Source/provenance

- Exact candidate/source manifest bound: **PASS**
- Automated provenance findings: **0**
- Refactor lineage from historical reviewed tree: **PASS**
- Historical Git identity/provenance preservation: **PASS**
- Bounded public-similarity review: **NO BLOCKER IDENTIFIED**
- Human factual provenance carry-forward: **RECORDED**

### Build/security/release engineering

- Candidate Windows regression/package gates: **PASS**
- Cross-platform refactor/package evidence: **PASS**
- Exact candidate build SBOM vs lock: **PASS**

### Legal/commercial distribution

- Executed author -> ООО rights evidence: **PENDING — BLOCKS APPROVED**
- Full third-party license-text bundle for promoted frozen artifacts: **PENDING — BLOCKS APPROVED COMMERCIAL ARTIFACT SET**
- AppImage commercial compliance: **EXCLUDED / HOLD UNTIL SEPARATELY CLEARED**
- Rospatent registration/transfer status: **AUTHORIZED FACT CONFIRMATION PENDING**
- Corporate transaction/approval basis where applicable: **AUTHORIZED FACT CONFIRMATION PENDING**

## 12. Final decision

**CONDITIONAL**

No source-code/provenance/public-similarity blocker was identified in the bounded post-refactor review. Final clean-IP `APPROVED` status and a clean-IP tag remain prohibited until:

1. the author -> ООО rights basis is executed/verified and referenced;
2. the promoted Windows/macOS/Linux `.deb` artifact set has the required complete third-party license/notice bundle staged and verified against actual shipped payloads;
3. AppImage remains excluded or receives a separate compliance clearance;
4. Rospatent registration/transfer status is factually resolved;
5. applicable corporate approval/interested-transaction basis is factually resolved;
6. an authorized human/legal reviewer records the final decision.

Any source change required by remediation invalidates the candidate and requires a new exact candidate/evidence binding. A documentation/package-compliance-only remediation must still be reviewed against its exact promoted release commit before tagging.

No clean-IP tag is authorized by this record.
