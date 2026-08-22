# Arvectum Proxy Launcher — canonical roadmap

Updated: 2026-08-22
Canonical branch: `main`
Current product version: `0.2.3`
Reconciliation base before this roadmap update: `e2be3445e23eb6e8f0709f37fec0ecba50447dc7`

Status legend:

- **DONE** — implementation and required acceptance are complete.
- **ACTIVE / CURRENT** — current execution priority.
- **READY / HOST AVAILABLE** — prerequisite environment exists and the task may be executed.
- **AUTONOMOUS COMPLETE / LOCAL ACCEPTANCE PENDING** — repository/CI work is complete; target-host proof remains.
- **HUMAN/LEGAL PENDING** — authorized factual/legal review remains.
- **CONDITIONAL** — bounded blockers remain; do not claim final approval.
- **DEFERRED / NOT RELEASE BLOCKER** — useful hardening outside the current critical path.
- **STOP-GATE** — do not implement production enforcement until the named decision is made.

## 0. Proven Windows/core baseline

- **DONE** — APL-CORE-007 unified backend contract & regression matrix.
- **DONE** — customer-proven Windows portable `0.2.3` system-proxy baseline.
- **DONE** — Windows runtime/security/diagnostics/productization CI.
- **DONE** — P0.1 controlled CPython `3.12.10` x64 + exact eight-wheel build-input archive.
- **DONE** — exact Inno Setup `6.7.1` controlled acquisition and canonical installer build.
- **DONE** — Russian-first owner-operated release provenance/signing contour with CryptoPro/Rutoken detached evidence.
- **CONSTRAINT** — sealed historical `0.2.3` evidence remains immutable.
- **CONSTRAINT** — per-application routing remains a separate enforcement plane.

### P0.2 independent clean-machine endpoint-denied rebuild

- **DEFERRED / NOT RELEASE BLOCKER**.
- A real physical x86-64 host exists, but Windows product acceptance has now progressed beyond the clean-machine point.
- Do not reinstall merely to satisfy P0.2. Run it later only if resilience/reproducibility assurance is promoted back to active priority.

## 1. Physical Windows acceptance stand — ARVECTUM-DEMO

Current physical stand:

- **DONE** — x86-64 physical laptop available.
- **DONE** — Windows 11 Enterprise 25H2 installed.
- **DONE** — portable `0.2.3` real-host functionality proven.
- **DONE** — installer transition defect #171 discovered on the real host rather than hidden by CI.
- **DONE** — PR #172 / merge `e2be3445e23eb6e8f0709f37fec0ecba50447dc7` fixes the defect fail-closed: deterministic portable rollback wait, installer maintenance preflight before install commit, regression coverage for portable-active -> installer transition and partial-install prevention.
- **DONE** — physical follow-up on ARVECTUM-DEMO: fixed RC installed over the previously problematic active-portable state with no errors/warnings; uninstall through Windows Installed Apps passed; fresh reinstall passed; persisted proxy settings survived; launcher works normally after reinstall.
- **DONE** — issue #171 closed from physical evidence.

### Physical installer / lifecycle acceptance

- **DONE — physical installer acceptance** for the defect-remediated RC on Windows 11 Enterprise 25H2.
- **DONE — uninstall/fresh-install control** on the physical stand.
- **DONE — state preservation check** across uninstall/reinstall for the tested configuration.
- The real-host finding and remediation are retained as regression evidence; future installer changes must continue to pass the #171 fail-closed transition contract.

### APL-WIN-014 — Windows application-control execution compatibility

- **ACTIVE / CURRENT — HOST ELIGIBLE**.
- ARVECTUM-DEMO runs Windows 11 Enterprise 25H2 and therefore satisfies the edition requirement for App Control for Business acceptance.
- Execute the canonical `docs/APL_WIN_014_LOCAL_GATE.md` matrix on this dedicated stand.
- Do not use the normal owner workstation for destructive application-control testing.
- After PASS, export/hash-verify evidence before changing the disk/boot layout.

### APL-REL-014 — exact signed-set lifecycle acceptance

- **PHYSICAL LIFECYCLE CORE PROVEN / FINAL EXACT-SET EVIDENCE RECONCILIATION PENDING IF REQUIRED BY THE CANONICAL REL-014 RECORD**.
- The physical host has now proven install-over-portable, uninstall, fresh reinstall and retained settings on the defect-remediated RC.
- Do not repeat destructive cycles merely for duplication. Reconcile the physical evidence against the exact governed release-set identity; run only any remaining canonical REL-014 step not already covered by the physical acceptance record.

### Persistent Windows + Astra dual-boot stand

Target final state: **UEFI/GPT Windows 11 + Astra Linux SE 1.8 x86-64 dual boot** on the 512 GB SSD.

Canonical runbook: `docs/PHYSICAL_WINDOWS_ASTRA_DUAL_BOOT_STAND.md`.

Remaining sequence:

1. **CURRENT — APL-WIN-014** on Windows 11 Enterprise 25H2;
2. reconcile/export/hash-verify remaining Windows acceptance evidence;
3. disable Fast Startup/hibernation and shrink `C:` safely from Windows;
4. keep existing EFI/MSR/Recovery/Windows partitions intact;
5. install Astra Linux SE 1.8 x86-64 into unallocated space using manual UEFI/GPT partitioning;
6. verify Windows Boot Manager and Astra both remain bootable;
7. capture clean Astra baseline;
8. execute APL-LNX-010 and close Gate R8 only from real Astra-host evidence;
9. retain both operating systems for regression.

## 2. Linux / Astra Linux

- **DONE** — APL-LNX-006 diagnostics/support bundle.
- **DONE** — APL-LNX-007 Debian `.deb` packaging.
- **DONE** — APL-LNX-008 AppImage packaging/toolchain engineering.
- **DONE** — APL-LNX-009 Ubuntu 22.04/24.04 CI acceptance.
- **DONE** — APL-IP-002-LNX conditional sovereignty audit.
- **READY / HOST AVAILABLE — NEXT AFTER WINDOWS GATE** — APL-LNX-010 real Astra Linux graphical/runtime/package acceptance.
- **LOCAL GATE** — Gate R8 closes only from real Astra evidence; Ubuntu CI is not a substitute.
- Preferred Astra distribution lane remains `.deb`.
- **HOLD** — AppImage is excluded from promoted commercial scope until L-2 downstream/type-2-runtime obligations are separately cleared.

## 3. macOS

- **DONE** — APL-MAC-001..008.
- **DONE** — APL-IP-002-MAC.
- **DONE** — Gate R9 real macOS acceptance.
- Apple production identity signing/notarization remains lower-priority distribution work under the Russia-first strategy.

## 4. Cross-platform sovereignty / IP

- **DONE** — APL-IP-002-WIN/LNX/MAC/FINAL.

### APL-IP-003 — canonical source refactor

- **ENGINEERING COMPLETE — SLICES 1–23 MERGED**.
- Immutable source-review anchor: `8ad54018e6d6251c906a06d09fd464c8931c14b2`.
- Legacy compatibility module/identity boundary retired; maintained source/repository/application layering guarded by permanent tests.
- No additional refactor slice is planned absent a concrete new finding.

### APL-IP-001 — post-refactor / post-APL-IP-004 review

- **CONDITIONAL / ENGINEERING RECONCILED / HUMAN-LEGAL PENDING**.
- **DONE — PR #170:** post-APL-IP-004 exact candidate/evidence reconciliation.
- Selected exact candidate: `ef9846e151a2e4e7046169e0787603969018cc97`, tree `98a09d821470a597715696e5ff3c7f376e5893a8`.
- Candidate-equivalent provenance/SBOM/package evidence rebound.
- **L-1 ENGINEERING-REMEDIATED** for newly built promoted Windows portable/installer, Debian `.deb`, and macOS `.app`/DMG.
- **L-2 HOLD** — AppImage excluded from promoted commercial scope.
- Remaining blockers before final `APPROVED`:
  1. **[Human] R-1** — execute/verify author -> ООО «Арвектум» rights basis;
  2. **[Human] R-2** — record actual Rospatent registration/transfer status;
  3. **[Human] R-3** — record applicable corporate/interested-transaction basis;
  4. **[Human]** confirm carried-forward factual provenance and sign final decision;
  5. **[Web after APPROVED]** create governed clean-IP baseline/tag.

### APL-IP-004 — third-party license bundle & promoted artifact compliance

- **ENGINEERING COMPLETE — merged PR #167**.
- Full third-party license bundle is fail-closed for newly built promoted Windows, Debian and macOS lanes.
- Historical artifacts are not retroactively relabeled.
- AppImage L-2 remains separate.

## 5. Per-application routing

- **DONE** — APL-ROUTE-001 rule model.
- **DONE** — APL-ROUTE-002 feasibility matrix.
- **AUTONOMOUS COMPLETE / LOCAL-NATIVE PENDING** — APL-ROUTE-003 control-plane prototype.
- **DONE** — APL-ROUTE-004 ownership/recovery/security journal.

### APL-ROUTE-003 production STOP-GATE

Before production Windows enforcement choose deliberately:

1. Microsoft Hardware Dev Center + accepted EV identity for an optional WFP/kernel SKU;
2. separately reviewed already-signed third-party enforcement component;
3. supported user-mode architecture with equivalent semantics;
4. defer Windows per-app routing while keeping system-proxy/domain/IP production-ready.

Test-signing/developer mode is not a production workaround.

## 6. Parallel execution model

### Track A — physical stand

1. **[Win] CURRENT — APL-WIN-014 App Control acceptance on Windows 11 Enterprise 25H2.**
2. **[Win] reconcile/export final Windows evidence.**
3. **[Win/Linux] prepare persistent dual boot.**
4. **[Linux] install Astra Linux SE 1.8 x86-64.**
5. **[Linux] APL-LNX-010 -> Gate R8.**

### Track B — IP / governance

1. **[Web] DONE — post-APL-IP-004 reconciliation.**
2. **[Human] CURRENT / PARALLEL — R-1/R-2/R-3 + authorized final sign-off.**
3. **[Web] after explicit APPROVED — clean-IP baseline/tag.**
4. **[Optional later] AppImage L-2 clearance.**

### Track C — product architecture

- **[Web/Decision] APL-ROUTE-003** may be researched in parallel; production enforcement remains STOP-GATE until a path is selected.

### Deferred hardening

- P0.2 clean-machine endpoint-denied rebuild;
- controlled Linux/macOS build-input mirrors and recovery builds;
- international Apple/Microsoft signing/notarization paths.

## 7. Immediate execution order

1. **[Win] APL-WIN-014 — real App Control for Business acceptance on ARVECTUM-DEMO.**
2. **[Human, parallel] R-1/R-2/R-3 + authorized IP sign-off.**
3. **[Win] export/reconcile all Windows stand evidence.**
4. **[Linux] create Astra dual boot -> APL-LNX-010 -> Gate R8.**
5. **[Web] clean-IP tag only after explicit `APPROVED`.**
6. **[Decision] APL-ROUTE-003 production enforcement path after canonical IP baseline is settled.**

## Completion rule

Real-host and human/legal gates remain pending until their named evidence exists. CI or documentation do not substitute for target-host proof or authorized legal/factual decisions. The dedicated ARVECTUM-DEMO laptop is the persistent Windows/Astra acceptance stand; the normal owner workstation remains protected from destructive acceptance work.
