# Arvectum Proxy Launcher — canonical roadmap

Updated: 2026-08-22
Canonical branch: `main`
Current product version: `0.2.3`
Reconciliation base before this roadmap update: `53f410f0211d8f29108c1c3e6365627e73c9da85`

Status legend:

- **DONE** — implementation and required acceptance are complete.
- **ACTIVE** — current execution priority.
- **READY / HOST AVAILABLE** — required physical host exists; execute when the named sequencing prerequisite is satisfied.
- **AUTONOMOUS COMPLETE / LOCAL ACCEPTANCE PENDING** — repository/CI work is complete; real target-host evidence is still required.
- **HUMAN/LEGAL PENDING** — engineering evidence exists, but authorized factual/legal review is still required.
- **CONDITIONAL** — review is complete enough to identify bounded remaining blockers; do not claim final approval.
- **DEFERRED / NOT RELEASE BLOCKER** — useful resilience/hardening work intentionally outside the current release critical path.
- **STOP-GATE** — do not continue production implementation until the named decision is made.

## 0. Proven Windows/core baseline

The customer-proven Windows `0.2.3` system-proxy path remains the protected production baseline.

- **DONE** — APL-CORE-007 unified backend contract & regression matrix.
- **DONE** — Windows portable/customer-confirmed `0.2.3` baseline.
- **DONE** — Windows runtime/security/diagnostics/productization CI.
- **DONE** — P0.1 controlled CPython `3.12.10` x64 + exact eight-wheel build-input archive and independent retained copy.
- **DONE** — exact Inno Setup `6.7.1` controlled acquisition and canonical production installer build.
- **DONE** — Russian-first owner-operated release provenance/signing contour using CryptoPro/Rutoken detached evidence; this does not claim embedded Authenticode/SmartScreen trust.
- **CONSTRAINT** — sealed `0.2.3` evidence remains immutable historical/release evidence.
- **CONSTRAINT** — per-application routing remains a separate enforcement plane and must not destabilize the proven system-proxy baseline.

### P0.2 independent clean-machine endpoint-denied rebuild

- **READY / HOST AVAILABLE — DEFERRED / NOT RELEASE BLOCKER**.
- A separate physical x86-64 laptop now exists, so the drill can be executed without reviving the abandoned VM path.
- The laptop currently starts from **Windows 10**, not Windows 11. For a canonical modern recovery proof, first move it to a supported Windows 11 configuration and, if the drill is executed, capture the clean Windows 11 baseline before product installation and before Astra/dual-boot repartitioning.
- Use governed P0.1 inputs, frozen source authority, endpoint denial, full tests/package contracts/SBOM and artifact comparison.
- If not executed before the laptop becomes dual boot, leave P0.2 deferred rather than forcing another reinstall.

## 1. Windows production / physical acceptance

### APL-WIN-014 — Windows application-control execution compatibility

- **READY / HOST AVAILABLE**, but the physical stand currently runs Windows 10.
- First inventory hardware/firmware and confirm official Windows 11 eligibility (UEFI, Secure Boot capability, TPM 2.0 and supported CPU).
- Upgrade or clean-install Windows 11 before canonical execution.
- `APL-WIN-014` requires Windows 11 **Pro, Enterprise or Education**. If the resulting edition is Home, upgrade/reinstall an eligible edition before App Control for Business acceptance.
- The normal owner workstation remains diagnostics-only; destructive App Control acceptance belongs only on the separate stand.
- Canonical runbook: `docs/APL_WIN_014_LOCAL_GATE.md`.

### APL-REL-014 — exact signed-set lifecycle acceptance

- **READY / HOST AVAILABLE** on the separate stand after the Windows 11 baseline is established.
- Execute fresh install, upgrade/repair, uninstall and rollback/recovery using the exact governed signed release set.
- Export/hash-verify all evidence before changing the Windows disk/boot layout for Astra.
- The owner workstation remains protected and is not the destructive acceptance target.

### Persistent Windows + Astra dual-boot stand

Target final state for the 512 GB SSD is **UEFI/GPT dual boot**, retaining both operating systems.

Canonical stand runbook: `docs/PHYSICAL_WINDOWS_ASTRA_DUAL_BOOT_STAND.md`.

Required sequence:

1. inventory current Windows 10 host and confirm Windows 11 eligibility;
2. upgrade or clean-install Windows 11; prefer Pro/Enterprise/Education for the full Windows gate set;
3. capture the clean Windows 11 baseline;
4. optionally execute P0.2 while the machine is still a Windows-only clean host;
5. execute APL-WIN-014 and APL-REL-014 as applicable;
6. export/hash-verify all Windows acceptance evidence;
7. disable Fast Startup/hibernation and safely shrink `C:` from Windows Disk Management;
8. install Astra Linux Special Edition 1.8 x86-64 into unallocated space using manual UEFI/GPT partitioning;
9. preserve the existing EFI System Partition and Windows Boot Manager; do not format Windows/MSR/Recovery partitions;
10. verify both Windows 11 and Astra remain bootable;
11. retain the laptop as a permanent dual-platform regression stand.

After Astra/GRUB installation the Windows side remains valid for regression, but it is no longer an untouched clean-machine baseline.

## 2. Linux / Astra Linux

- **DONE** — APL-LNX-006 diagnostics/support bundle.
- **DONE** — APL-LNX-007 Debian `.deb` packaging.
- **DONE** — APL-LNX-008 AppImage packaging/toolchain engineering.
- **DONE** — APL-LNX-009 Ubuntu 22.04/24.04 CI acceptance.
- **DONE** — APL-IP-002-LNX conditional sovereignty audit.
- **READY / HOST AVAILABLE** — APL-LNX-010 real Astra Linux graphical/runtime/package acceptance. The physical x86-64 laptop is allocated for Astra after the Windows-only evidence phase.
- **LOCAL GATE** — Gate R8 closes only from real Astra-host evidence; Ubuntu CI or another distro is not a substitute.
- Preferred controlled Astra distribution lane remains `.deb`.
- **HOLD** — AppImage is not cleared for promoted commercial distribution until the separate L-2 downstream/type-2-runtime compliance obligations are explicitly closed.

## 3. macOS

- **DONE** — APL-MAC-001..008.
- **DONE** — APL-IP-002-MAC.
- **DONE** — Gate R9 real macOS acceptance.
- Apple production identity signing/notarization remains a later distribution-policy task under the Russia-first strategy.

## 4. Cross-platform sovereignty / IP

- **DONE** — APL-IP-002-WIN/LNX/MAC/FINAL.

### APL-IP-003 — canonical source refactor

- **ENGINEERING COMPLETE — SLICES 1–23 MERGED**.
- Exact engineering-completion/source-review anchor: `8ad54018e6d6251c906a06d09fd464c8931c14b2`.
- Legacy `proxy_core_legacy.py` and the old module-identity compatibility boundary are retired.
- Historical stdlib façade aliases were reduced to zero.
- Current maintained production source, regression naming, repository identity and GUI/backend layering are guarded by permanent tests.
- Final Slice 23 candidate evidence included 640 Windows tests and successful canonical-source/provenance/SBOM/security/Windows packaging gates; preceding Slice 22 supplied the full cross-platform matrix.
- No additional APL-IP-003 engineering slice is planned unless a concrete review finding requires technical remediation.

### APL-IP-001 — post-refactor / post-APL-IP-004 review

- **CONDITIONAL / POST-APL-IP-004 ENGINEERING RECONCILED / HUMAN-LEGAL PENDING**.
- Original post-refactor review packet merged in PR #166 and remains the source-review evidence for the unchanged 45-file significant product-source set.
- Immutable source-review anchor: `8ad54018e6d6251c906a06d09fd464c8931c14b2`, tree `eac5db739e7bd3fda595b09b2ec869ad06a87ba3`.
- **Selected exact post-APL-IP-004 candidate:** `ef9846e151a2e4e7046169e0787603969018cc97`, tree `98a09d821470a597715696e5ff3c7f376e5893a8`.
- Final PR #167 head `ab3f6aea8087ac09c3d8dcbdf348fcc7f6684f9f`, PR test-merge `818a39591cd2377bd1c451294854d4f787a9f369` and selected candidate have the identical tree `98a09d821470a597715696e5ff3c7f376e5893a8`.
- No file in the 45-file significant product-source set changed between the source-review anchor and selected candidate; the bounded public-similarity/source review is therefore carried forward for that unchanged set.
- Candidate-equivalent provenance was regenerated: manifest SHA-256 `baf27272def4c03c7f44852ff11aa1c2fdb32710f92ac0e322f94b557158a87b`, **377 governed records**, **45 product-source records**, automated provenance-marker findings **0**.
- Candidate-equivalent build SBOM was regenerated/rebound; CycloneDX SHA-256 remains `fccd5d2d94a4c2f8ebbc9fdde709db5b0fd1ae13f962f9046d706086a345ac4a` because the frozen build lock did not change.
- **L-1 ENGINEERING-REMEDIATED** for newly built promoted Windows portable, Windows installer, Debian `.deb`, and macOS `.app`/DMG artifacts. Windows installer acceptance was explicitly rerun after the original concurrency cancellation and passed compile, lifecycle E2E and Gate R6.
- **L-2 HOLD:** AppImage remains excluded from promoted commercial scope pending separate type-2-runtime/transitive compliance clearance.
- Canonical reconciliation evidence: `docs/evidence/APL_IP_001_POST_IP_004_CANDIDATE_RECONCILIATION_2026-08-22.md`.
- Canonical current sign-off: `docs/APL_IP_001_POST_REFACTOR_SIGNOFF.md`.
- R-1 execution draft is rebound to the same selected candidate: `docs/legal/APL_IP_001_RIGHTS_ASSIGNMENT_POST_REFACTOR_2026-08-22.md`.

Remaining human/legal blockers before final `APPROVED`:

1. **[Human] R-1** — execute/verify the author → ООО «Арвектум» rights basis for the selected `ef9846e...` candidate and retain a stable non-secret evidence reference;
2. **[Human] R-2** — record the actual Rospatent registration/transfer status applicable at review time;
3. **[Human] R-3** — record the actual corporate/interested-transaction basis or approval/exception where applicable;
4. **[Human]** confirm carried-forward factual provenance for the selected candidate and sign the final decision;
5. **[Web after explicit APPROVED]** create the governed clean-IP baseline/tag only for the exact approved candidate.

### APL-IP-004 — third-party license bundle & promoted artifact compliance

- **ENGINEERING COMPLETE — merged PR #167** at merge commit `ef9846e151a2e4e7046169e0787603969018cc97`.
- Finding L-1 is engineering-remediated for **newly built promoted Windows portable, Windows installer, Debian `.deb`, and macOS `.app`/DMG** artifacts through a fail-closed full third-party license bundle generated from the exact build environment.
- Required bundle includes governed full license/copyright texts for Python, Tcl, Tk and PyInstaller plus SHA-256 manifest verification.
- Windows portable, Windows installer, Debian and macOS package lanes are accepted on the candidate-equivalent PR tree; historical release artifacts are not retroactively relabeled.
- **L-2 remains HOLD:** AppImage is still excluded from promoted commercial scope until pinned type-2 runtime/transitive obligations, including applicable LGPL/libfuse path, are separately cleared.
- APL-IP-004 is an engineering compliance control, not final legal approval.

### Final clean-IP candidate rule after APL-IP-004

The selected clean-IP/commercial candidate is now **`ef9846e151a2e4e7046169e0787603969018cc97` / tree `98a09d821470a597715696e5ff3c7f376e5893a8`**. The older `8ad54018...` commit remains the immutable APL-IP-003/source-review anchor and must not be tagged as if it contained APL-IP-004.

Documentation-only reconciliation commits after `ef9846e...` do not silently replace the selected product/package candidate. However, any change to product source, build dependencies, packaging/compliance implementation or selected promoted-artifact contents requires a new exact candidate/evidence binding before clean-IP approval/tagging.

## 5. Per-application routing

- **DONE** — APL-ROUTE-001 rule model.
- **DONE** — APL-ROUTE-002 feasibility matrix.
- **AUTONOMOUS COMPLETE / LOCAL-NATIVE PENDING** — APL-ROUTE-003 control-plane prototype.
- **DONE** — APL-ROUTE-004 ownership/recovery/security journal.

### APL-ROUTE-003 production STOP-GATE

Before production Windows native enforcement choose deliberately:

1. Microsoft Hardware Dev Center + accepted EV identity for an optional WFP/kernel SKU;
2. separately reviewed already-signed third-party enforcement component;
3. supported user-mode architecture with equivalent semantics;
4. defer Windows per-app routing while keeping system-proxy/domain/IP production-ready.

Test-signing/developer modes are not accepted as a production workaround.

## 6. Parallel execution model

### Track A — IP / governance

1. **[Web] DONE — post-APL-IP-004 review reconciliation:** exact candidate selected and provenance, SBOM and promoted-artifact license evidence rebound; L-1 is engineering-remediated without claiming legal approval.
2. **[Human] ACTIVE / PARALLEL — R-1/R-2/R-3 + authorized sign-off:** rights basis, Rospatent status, corporate basis, carried-forward factual provenance and final factual/legal decision.
3. **[Web] after explicit APPROVED — clean-IP baseline/tag.**
4. **[Optional later] AppImage L-2 clearance** only if AppImage is to enter promoted commercial scope.

### Track B — physical Windows/Astra stand

1. **[Win] ACTIVE — Windows 11 stand preparation/baseline.**
2. **[Win] optional P0.2** before product installation/repartitioning if still desired.
3. **[Win] APL-WIN-014** real application-control acceptance.
4. **[Win] APL-REL-014** exact signed-set lifecycle acceptance.
5. **[Win] export/hash-verify evidence.**
6. **[Win/Linux] partition 512 GB SSD for persistent dual boot** without deleting Windows.
7. **[Linux] install Astra Linux SE 1.8 x86-64 and capture clean baseline.**
8. **[Linux] APL-LNX-010 → Gate R8.**
9. retain both OSes for future regression.

### Track C — product architecture

- **[Web/Decision] APL-ROUTE-003** may be researched in parallel, but production native enforcement remains STOP-GATE until the product/signing path is explicitly selected.

### Deferred hardening

- controlled Linux/macOS build-input mirrors and endpoint-denied rebuild proofs;
- international Apple/Microsoft signing/notarization paths;
- P0.2 if not completed during the clean Windows-only phase.

## 7. Immediate execution order

1. **[Human, parallel] execute/verify R-1/R-2/R-3, confirm carried-forward provenance facts and complete authorized final sign-off.**
2. **[Win, parallel] continue the physical Windows 11 stand baseline/preparation.**
3. **[Win] APL-WIN-014 + APL-REL-014** after the Windows 11 baseline exists.
4. **[Linux] Astra dual boot → APL-LNX-010 → Gate R8** after Windows-only evidence is exported.
5. **[Web] clean-IP tag** only after explicit `APPROVED` on the exact post-APL-IP-004 candidate.
6. **[Decision] APL-ROUTE-003** production enforcement path after the canonical IP baseline is settled.

## Completion rule

Real-host, signing, external-platform and human/legal gates remain pending until their named evidence exists. CI, documentation or hashes do not substitute for authorized factual/legal decisions. Historical evidence remains truthful and immutable; newer compliance controls must not be retroactively attributed to older artifacts. The normal owner Windows workstation remains protected from destructive WIN-014/REL-014 acceptance. The dedicated physical laptop is the Windows/Astra dual-platform acceptance stand.
