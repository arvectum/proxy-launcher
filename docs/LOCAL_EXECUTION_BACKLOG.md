# Arvectum Proxy Launcher — remaining local / human / infrastructure backlog

Updated: 2026-08-22

This file contains work that cannot be truthfully completed by hosted repository automation alone. The protected customer-proven Windows `0.2.3` system-proxy baseline remains the behavioral reference.

## P0 — Windows physical acceptance stand

A separate x86-64 laptop with a 512 GB SSD is now available. Its current OS is **Windows 10**. The intended permanent end state is **Windows 11 + Astra Linux Special Edition 1.8 x86-64 dual boot**.

Canonical stand runbook: `docs/PHYSICAL_WINDOWS_ASTRA_DUAL_BOOT_STAND.md`.

### P0.1 Controlled Windows build inputs — DONE

Status: **DONE / CLOSED**.

Canonical governed archive:

- `arvectum-windows-build-inputs-cpython-3.12.10-x64.zip`;
- bytes: `30996168`;
- SHA-256: `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`;
- CPython `3.12.10` x64;
- exactly eight approved Windows x64 wheels;
- canonical evidence: `docs/evidence/P0_1_COMPLETION_EVIDENCE.json`.

### P0.2 Independent clean-machine endpoint-denied rebuild — READY BUT DEFERRED

Status: **READY / HOST AVAILABLE — DEFERRED / NOT RELEASE BLOCKER**.

If executed on the new laptop:

1. first prove official Windows 11 eligibility and move the machine from Windows 10 to Windows 11;
2. preferably use a clean/reset Windows 11 baseline;
3. execute before installing Proxy Launcher for lifecycle tests and before changing the disk to dual boot;
4. use only governed P0.1 CPython/wheelhouse inputs plus the frozen source authority;
5. deny public package/source endpoints during the recovery build;
6. run full tests, package contracts, SBOM and artifact comparison;
7. export evidence outside the stand.

If this window is missed, keep P0.2 deferred rather than forcing another reinstall. The abandoned VM path remains historical evidence only.

### P0.3 Windows 10 → Windows 11 stand preparation — ACTIVE

Required local boundary:

1. record hardware/firmware inventory;
2. verify UEFI/Secure Boot capability, TPM 2.0 and supported CPU;
3. preserve any BitLocker/device-encryption recovery material before firmware/disk changes;
4. upgrade or clean-install Windows 11;
5. for full APL-WIN-014 coverage, use Windows 11 Pro, Enterprise or Education;
6. capture the clean Windows 11 baseline before product installation.

### P0.4 APL-WIN-014 real App Control acceptance — READY AFTER P0.3

Repository tooling is complete. Real completion requires the separate Windows 11 Pro/Enterprise/Education stand.

Do not execute destructive policy work on the normal owner workstation.

### P0.5 APL-REL-014 exact signed-set lifecycle acceptance — READY AFTER P0.3

On the same physical stand execute the exact governed release set through:

- fresh install;
- upgrade/repair;
- uninstall;
- rollback/recovery;
- final diagnostics/evidence collection.

Export and hash-verify evidence before Linux repartitioning.

## P1 — Astra Linux real acceptance / Gate R8

Status: **READY / HOST AVAILABLE AFTER WINDOWS-ONLY PHASE**.

The same physical laptop becomes a persistent dual-boot Linux stand without deleting Windows.

Required sequence:

1. complete/export any Windows clean-host evidence first;
2. disable Windows Fast Startup/hibernation;
3. shrink Windows `C:` from Windows Disk Management and leave Linux space unallocated;
4. install Astra Linux Special Edition 1.8 x86-64 using manual GPT/UEFI partitioning;
5. preserve existing EFI System Partition, Windows NTFS, MSR and Recovery partitions;
6. create Astra ext4 root in the unallocated space;
7. verify both Windows Boot Manager and Astra boot successfully;
8. capture clean Astra baseline;
9. run `bash qa/collect_astra_acceptance_preflight.sh`;
10. execute APL-LNX-010 real `.deb` acceptance matrix;
11. close Gate R8 only from real Astra-host PASS evidence.

Ubuntu CI or another distro is not a substitute.

## P2 — APL-IP-001 final post-refactor human/legal sign-off

Status: **CONDITIONAL / HUMAN-LEGAL PENDING**.

Engineering state:

- APL-IP-003 Slices 1–23: complete;
- refactor-review anchor candidate: `8ad54018e6d6251c906a06d09fd464c8931c14b2`;
- post-refactor review packet: merged PR #166;
- APL-IP-004 promoted-artifact license-bundle engineering remediation: merged PR #167;
- AppImage L-2 commercial-promotion hold remains.

Required human/legal boundary:

1. execute/verify author → ООО «Арвектум» rights basis (R-1);
2. record actual Rospatent registration/transfer status (R-2);
3. record applicable corporate/interested-transaction basis/approval/exception (R-3);
4. confirm factual post-refactor provenance;
5. select the promoted artifact scope;
6. sign an explicit final `APPROVED`, `CONDITIONAL` or `HOLD` decision.

Because APL-IP-004 changed compliance tooling after the APL-IP-003 review anchor, final clean-IP approval must be rebound to a new exact **post-APL-IP-004** candidate and current evidence. Do not tag `8ad54018...` as if it contained APL-IP-004.

After explicit `APPROVED`, hosted repository work may create the governed clean-IP baseline/tag.

## P3 — AppImage L-2 downstream compliance — OPTIONAL / HOLD

AppImage remains excluded from promoted commercial scope until the pinned type-2 runtime/transitive obligations are separately reviewed and packaged, including the applicable LGPL/libfuse path and other statically linked runtime components.

This does not block `.deb` as the preferred Astra/Linux distribution lane.

## P4 — APL-ROUTE-003 Windows per-application routing product decision

Production WFP connect-redirection remains a STOP-GATE until one path is chosen:

1. Microsoft Hardware Dev Center + accepted EV identity dependency;
2. separately reviewed already-signed third-party component;
3. supported user-mode architecture with equivalent semantics;
4. defer Windows per-app routing.

Do not use test-signing/developer mode as a production workaround.

## P5 — controlled Linux/macOS build-input mirrors

Status: **DEFERRED / MEDIUM PRIORITY**.

- archive pinned platform build inputs;
- add immutable hashes/recovery instructions;
- run endpoint-denied rebuild proofs when useful.

## Current parallel execution order

### Track A — repository/IP

1. **[Web] select/rebind a post-APL-IP-004 exact candidate and regenerate current provenance/SBOM/promoted-artifact evidence.**
2. **[Human] in parallel complete R-1/R-2/R-3 and authorized final sign-off facts.**
3. **[Web] create clean-IP baseline/tag only after explicit APPROVED.**

### Track B — physical laptop

1. **[Win] inventory Windows 10 and prove Windows 11 eligibility.**
2. **[Win] upgrade/clean-install Windows 11; target Pro/Enterprise/Education.**
3. **[Win] optional P0.2 before product/repartitioning.**
4. **[Win] APL-WIN-014 and APL-REL-014.**
5. **[Win] export evidence.**
6. **[Win/Linux] create persistent dual boot.**
7. **[Linux] Astra SE 1.8 → APL-LNX-010 → Gate R8.**

### Track C — architecture decision

- **[Web/Decision] APL-ROUTE-003** may be researched in parallel but production native enforcement remains blocked pending the explicit product/signing choice.

## Completion discipline

Do not relabel real-host or human/legal gates as complete from CI, mocks or documentation. Do not retroactively attribute newer APL-IP-004 compliance controls to historical artifacts. Preserve the normal owner workstation from destructive WIN-014/REL-014 testing.