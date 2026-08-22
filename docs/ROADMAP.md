# Arvectum Proxy Launcher — canonical roadmap

Updated: 2026-08-22
Canonical branch: `main`
Current product version: `0.2.3`
Reconciled repository head before this roadmap update: `ef9846e151a2e4e7046169e0787603969018cc97`

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
- Exact engineering-completion candidate: `8ad54018e6d6251c906a06d09fd464c8931c14b2`.
- Legacy `proxy_core_legacy.py` and the old module-identity compatibility boundary are retired.
- Historical stdlib façade aliases were reduced to zero.
- Current maintained production source, regression naming, repository identity and GUI/backend layering are guarded by permanent tests.
- Final Slice 23 candidate evidence included 640 Windows tests and successful canonical-source/provenance/SBOM/security/Windows packaging gates; preceding Slice 22 supplied the full cross-platform matrix.
- No additional APL-IP-003 engineering slice is planned unless a concrete review finding requires technical remediation.

### APL-IP-001 — post-refactor review

- **CONDITIONAL / HUMAN-LEGAL PENDING**.
- Post-refactor review packet merged in PR #166.
- Reviewed source-refactor candidate: `8ad54018e6d6251c906a06d09fd464c8931c14b2`.
- Current post-refactor product-source review set: **45 files**.
- Automated provenance-marker findings: **0**.
- Public-similarity review found no identified source blocker in the bounded representative set.
- Build SBOM/provenance/platform evidence was regenerated and reconciled.
- Canonical current sign-off: `docs/APL_IP_001_POST_REFACTOR_SIGNOFF.md`.

Remaining human/legal blockers before final `APPROVED`:

1. **[Human] R-1** — execute/verify the author → ООО «Арвектум» rights basis and retain a stable non-secret evidence reference;
2. **[Human] R-2** — record the actual Rospatent registration/transfer status applicable at review time;
3. **[Human] R-3** — record the actual corporate/interested-transaction basis or approval/exception where applicable;
4. **[Human]** confirm post-refactor factual provenance and sign the final decision;
5. **[Web after approval]** create the governed clean-IP baseline/tag only for the exact approved candidate.

### APL-IP-004 — third-party license bundle & promoted artifact compliance

- **ENGINEERING DONE — merged PR #167** at merge commit `ef9846e151a2e4e7046169e0787603969018cc97`.
- Finding L-1 is engineering-remediated for **newly built promoted Windows portable, Windows installer, Debian `.deb`, and macOS `.app`/DMG** artifacts through a fail-closed full third-party license bundle generated from the exact build environment.
- Required bundle includes governed full license/copyright texts for Python, Tcl, Tk and PyInstaller plus SHA-256 manifest verification.
- Windows portable, Debian, AppImage, macOS packaging and core security/provenance workflows were green on the final implementation head; historical release artifacts are not retroactively relabeled.
- **L-2 remains HOLD:** AppImage is still excluded from promoted commercial scope until pinned type-2 runtime/transitive obligations, including applicable LGPL/libfuse path, are separately cleared.
- APL-IP-004 is an engineering compliance control, not final legal approval.

### Final clean-IP candidate rule after APL-IP-004

The APL-IP-003 candidate remains the immutable refactor-review anchor, but APL-IP-004 changed promoted-artifact compliance source/tooling after that candidate. Therefore the final clean-IP/commercial sign-off must bind to a **new exact post-APL-IP-004 candidate** and updated evidence before `APPROVED`/tagging. Do not tag the older `8ad54018...` candidate as if it contained APL-IP-004.

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

1. **[Web] ACTIVE — post-APL-IP-004 review reconciliation:** select a new exact candidate and regenerate/rebind provenance, SBOM and promoted-artifact license evidence; update L-1 from pending to engineering-remediated in the canonical post-refactor sign-off without claiming legal approval.
2. **[Human] PARALLEL — R-1/R-2/R-3 + authorized sign-off:** rights basis, Rospatent status, corporate basis and final factual/legal decision.
3. **[Web] after explicit APPROVED — clean-IP baseline/tag.**
4. **[Optional later] AppImage L-2 clearance** only if AppImage is to enter promoted commercial scope.

### Track B — physical Windows/Astra stand

1. **[Win] ACTIVE — inventory Windows 10 stand and prove Windows 11 eligibility.**
2. **[Win] upgrade/clean-install Windows 11**; target Pro/Enterprise/Education for full APL-WIN-014 coverage.
3. **[Win] optional P0.2** before product installation/repartitioning.
4. **[Win] APL-WIN-014** real application-control acceptance.
5. **[Win] APL-REL-014** exact signed-set lifecycle acceptance.
6. **[Win] export/hash-verify evidence.**
7. **[Win/Linux] partition 512 GB SSD for persistent dual boot** without deleting Windows.
8. **[Linux] install Astra Linux SE 1.8 x86-64 and capture clean baseline.**
9. **[Linux] APL-LNX-010 → Gate R8.**
10. retain both OSes for future regression.

### Track C — product architecture

- **[Web/Decision] APL-ROUTE-003** may be researched in parallel, but production native enforcement remains STOP-GATE until the product/signing path is explicitly selected.

### Deferred hardening

- controlled Linux/macOS build-input mirrors and endpoint-denied rebuild proofs;
- international Apple/Microsoft signing/notarization paths;
- P0.2 if not completed during the clean Windows-only phase.

## 7. Immediate execution order

1. **[Web] post-APL-IP-004 candidate/evidence reconciliation for APL-IP-001.**
2. **[Human, parallel] execute/verify R-1/R-2/R-3 and authorized final sign-off facts.**
3. **[Win, parallel] prepare the physical Windows 10 laptop for Windows 11 canonical acceptance.**
4. **[Win] APL-WIN-014 + APL-REL-014** after the Windows 11 baseline exists.
5. **[Linux] Astra dual boot → APL-LNX-010 → Gate R8** after Windows-only evidence is exported.
6. **[Web] clean-IP tag** only after explicit APPROVED on the exact post-APL-IP-004 candidate.
7. **[Decision] APL-ROUTE-003** production enforcement path after the canonical IP baseline is settled.

## Completion rule

Real-host, signing, external-platform and human/legal gates remain pending until their named evidence exists. CI, documentation or hashes do not substitute for authorized factual/legal decisions. Historical evidence remains truthful and immutable; newer compliance controls must not be retroactively attributed to older artifacts. The normal owner Windows workstation remains protected from destructive WIN-014/REL-014 acceptance. The dedicated physical laptop is the Windows/Astra dual-platform acceptance stand.