# Arvectum Proxy Launcher — canonical roadmap

Updated: 2026-08-22
Canonical branch: `main`
Current product version: `0.2.3`

Status legend:

- **DONE** — implementation and required acceptance are complete.
- **CURRENT** — current active task.
- **READY / HOST AVAILABLE** — required physical host exists; execute when sequencing allows.
- **AUTONOMOUS COMPLETE / LOCAL ACCEPTANCE PENDING** — repository/CI work is complete; real target-host evidence is still required.
- **HUMAN/LEGAL PENDING** — engineering evidence exists, but authorized factual/legal review is still required.
- **CONDITIONAL** — bounded blockers remain; do not claim final approval.
- **DEFERRED / NOT RELEASE BLOCKER** — useful resilience/hardening work outside the current release critical path.
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
- A separate physical x86-64 laptop exists and now runs Windows 11.
- If this drill is deliberately executed, use governed P0.1 inputs, frozen source authority, endpoint denial, full tests/package contracts/SBOM and artifact comparison.
- Do not interrupt the current physical installer acceptance to revive P0.2; if not completed before Astra dual boot, keep it deferred rather than forcing a reinstall.

## 1. Dedicated physical Windows/Astra acceptance stand

A separate x86-64 laptop with a 512 GB SSD is now the persistent physical acceptance stand.

### Current stand state

- **DONE — [Win] Windows 11 installed** on the physical stand.
- **DONE — [Win] Windows portable real-host acceptance:** the portable Arvectum Proxy Launcher version has been proven operational on this physical Windows 11 host.
- **CURRENT — [Win] Windows installer/full-version real-host acceptance:** the installed/full version is being tested now. Do not mark this task PASS until install/start/core proxy behavior and the intended lifecycle checks are actually confirmed.
- **NEXT — [Win] complete remaining Windows physical gates/evidence** after installer acceptance, including APL-REL-014 lifecycle coverage and APL-WIN-014 if the installed Windows edition is eligible for the App Control for Business gate.
- **NEXT — [Win/Linux] only after Windows evidence is exported and hash-verified, repartition the SSD and install Astra Linux alongside Windows in persistent UEFI/GPT dual boot.**
- **NEXT — [Linux] APL-LNX-010 real Astra acceptance → Gate R8.**

The previous Windows 10 → Windows 11 migration step is complete and must no longer appear as pending work.

### Windows installer/full-version acceptance — current task

Current acceptance target is the real installed product on the physical Windows 11 stand.

Minimum evidence before marking the current task PASS:

1. installer launches and completes successfully;
2. installed application starts successfully from the installed location/normal user entry point;
3. core system-proxy functionality works on the real host at the same protected `0.2.3` behavioral baseline;
4. disable/rollback restores the expected pre-product proxy state;
5. application survives at least one normal close/reopen cycle;
6. uninstall/lifecycle behavior is executed under APL-REL-014 rather than inferred from a successful installation alone;
7. diagnostics/evidence needed for the physical acceptance are exported outside the stand.

A successful installer launch alone is not equivalent to full lifecycle acceptance.

### APL-WIN-014 — Windows application-control execution compatibility

- **READY / HOST AVAILABLE** on the Windows 11 stand, subject to edition eligibility.
- APL-WIN-014 requires Windows 11 **Pro, Enterprise or Education** for the intended App Control for Business gate.
- If the stand edition is Home, do not force App Control policy deployment; retain the stand for installer/lifecycle acceptance and upgrade/reinstall an eligible edition only if WIN-014 is to be closed on this machine.
- The normal owner workstation remains diagnostics-only; destructive App Control acceptance belongs only on this separate stand.
- Canonical runbook: `docs/APL_WIN_014_LOCAL_GATE.md`.

### APL-REL-014 — exact signed-set lifecycle acceptance

- **READY / HOST AVAILABLE; follows the current installer functionality check.**
- Execute fresh install, upgrade/repair as applicable, uninstall and rollback/recovery using the exact governed signed release set.
- Export/hash-verify all evidence before changing the disk/boot layout for Astra.

### Persistent Windows + Astra dual boot

Target final state for the 512 GB SSD is **UEFI/GPT dual boot**, retaining Windows 11 and Astra Linux.

Canonical stand runbook: `docs/PHYSICAL_WINDOWS_ASTRA_DUAL_BOOT_STAND.md`.

Updated physical sequence:

1. **DONE:** Windows 11 installation;
2. **DONE:** portable real-host functionality proof;
3. **CURRENT:** installed/full-version functionality proof;
4. complete APL-REL-014 and APL-WIN-014 as applicable;
5. export/hash-verify all Windows acceptance evidence;
6. disable Fast Startup/hibernation and safely shrink `C:` from Windows Disk Management;
7. install Astra Linux Special Edition 1.8 x86-64 into unallocated space using manual UEFI/GPT partitioning;
8. preserve the existing EFI System Partition and Windows Boot Manager; do not format Windows/MSR/Recovery partitions;
9. verify both Windows 11 and Astra remain bootable;
10. execute APL-LNX-010 / Gate R8;
11. retain both operating systems for future regression.

After Astra/GRUB installation the Windows side remains valid for regression, but it is no longer an untouched clean-machine baseline.

## 2. Linux / Astra Linux

- **DONE** — APL-LNX-006 diagnostics/support bundle.
- **DONE** — APL-LNX-007 Debian `.deb` packaging.
- **DONE** — APL-LNX-008 AppImage packaging/toolchain engineering.
- **DONE** — APL-LNX-009 Ubuntu 22.04/24.04 CI acceptance.
- **DONE** — APL-IP-002-LNX conditional sovereignty audit.
- **READY / HOST AVAILABLE** — APL-LNX-010 real Astra Linux graphical/runtime/package acceptance. The physical x86-64 laptop is allocated for Astra after the Windows physical-evidence phase.
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
- Historical stdlib facade aliases were reduced to zero.
- Current maintained production source, regression naming, repository identity and GUI/backend layering are guarded by permanent tests.
- No additional APL-IP-003 engineering slice is planned unless a concrete review finding requires technical remediation.

### APL-IP-001 — post-refactor review

- **CONDITIONAL / HUMAN-LEGAL PENDING**.
- Post-refactor review packet merged in PR #166.
- Reviewed source-refactor candidate: `8ad54018e6d6251c906a06d09fd464c8931c14b2`.
- Current post-refactor product-source review set: 45 files.
- Automated provenance-marker findings: 0.
- Public-similarity review found no identified source blocker in the bounded representative set.
- Canonical current sign-off: `docs/APL_IP_001_POST_REFACTOR_SIGNOFF.md`.

Remaining human/legal blockers before final `APPROVED`:

1. **[Human] R-1** — execute/verify the author → ООО «Арвектум» rights basis and retain a stable non-secret evidence reference;
2. **[Human] R-2** — record the actual Rospatent registration/transfer status applicable at review time;
3. **[Human] R-3** — record the actual corporate/interested-transaction basis or approval/exception where applicable;
4. **[Human]** confirm post-refactor factual provenance and sign the final decision;
5. **[Web after approval]** create the governed clean-IP baseline/tag only for the exact approved candidate.

### APL-IP-004 — third-party license bundle & promoted artifact compliance

- **ENGINEERING DONE — merged PR #167** at merge commit `ef9846e151a2e4e7046169e0787603969018cc97`.
- Finding L-1 is engineering-remediated for newly built promoted Windows portable, Windows installer, Debian `.deb`, and macOS `.app`/DMG artifacts through a fail-closed full third-party license bundle generated from the exact build environment.
- **L-2 remains HOLD:** AppImage is still excluded from promoted commercial scope until pinned type-2 runtime/transitive obligations are separately cleared.
- APL-IP-004 is an engineering compliance control, not final legal approval.

### Final clean-IP candidate rule after APL-IP-004

The APL-IP-003 candidate remains the immutable refactor-review anchor, but APL-IP-004 changed promoted-artifact compliance source/tooling after that candidate. Therefore final clean-IP/commercial sign-off must bind to a **new exact post-APL-IP-004 candidate** and updated evidence before `APPROVED`/tagging.

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

### Track A — physical Windows/Astra stand

1. **[Win] DONE — Windows 11 installed.**
2. **[Win] DONE — portable real-host functionality proof.**
3. **[Win] CURRENT — installed/full-version functionality proof.**
4. **[Win] NEXT — APL-REL-014 lifecycle acceptance; APL-WIN-014 if edition eligible.**
5. **[Win] export/hash-verify Windows evidence.**
6. **[Win/Linux] partition SSD for persistent dual boot without deleting Windows.**
7. **[Linux] install Astra Linux SE 1.8 x86-64 and capture clean baseline.**
8. **[Linux] APL-LNX-010 → Gate R8.**
9. retain both OSes for future regression.

### Track B — IP / governance

1. **[Web] ACTIVE — post-APL-IP-004 review reconciliation:** select a new exact candidate and regenerate/rebind provenance, SBOM and promoted-artifact license evidence.
2. **[Human] PARALLEL — R-1/R-2/R-3 + authorized sign-off.**
3. **[Web] after explicit APPROVED — clean-IP baseline/tag.**
4. **[Optional later] AppImage L-2 clearance** only if AppImage is to enter promoted commercial scope.

### Track C — product architecture

- **[Web/Decision] APL-ROUTE-003** may be researched in parallel, but production native enforcement remains STOP-GATE until the product/signing path is explicitly selected.

### Deferred hardening

- P0.2 if not deliberately completed before Astra dual boot;
- controlled Linux/macOS build-input mirrors and endpoint-denied rebuild proofs;
- international Apple/Microsoft signing/notarization paths.

## 7. Immediate execution order

1. **[Win] CURRENT — complete real-host functionality check of the installed/full Windows version on the physical Windows 11 stand.**
2. **[Win] APL-REL-014**, then **APL-WIN-014** if edition eligible; export/hash-verify evidence.
3. **[Linux] Astra dual boot → APL-LNX-010 → Gate R8.**
4. **[Web, parallel] post-APL-IP-004 candidate/evidence reconciliation for APL-IP-001.**
5. **[Human, parallel] execute/verify R-1/R-2/R-3 and authorized final sign-off facts.**
6. **[Web] clean-IP tag** only after explicit APPROVED on the exact post-APL-IP-004 candidate.
7. **[Decision] APL-ROUTE-003** production enforcement path after the canonical IP baseline is settled.

## Completion rule

Real-host, signing, external-platform and human/legal gates remain pending until their named evidence exists. A successful portable test does not substitute for installed-product lifecycle acceptance; a successful installer launch does not substitute for uninstall/rollback/recovery evidence. Historical evidence remains truthful and immutable. The dedicated physical laptop is the Windows/Astra dual-platform acceptance stand.