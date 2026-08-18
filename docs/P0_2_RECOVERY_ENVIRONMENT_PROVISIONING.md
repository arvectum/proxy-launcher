# P0.2 — disposable Windows x64 recovery environment provisioning

Status: **CLEAN BASELINE PASS / CONTROLLED INPUT STAGING PENDING**.

The dedicated VirtualBox recovery environment now contains a clean Windows 11 Enterprise Evaluation 25H2 x64 guest and a verified `P0-2-CLEAN-BASELINE` snapshot created before any Proxy Launcher source, P0.1 archive or project build dependencies were introduced. The endpoint-denied portable recovery proof has not yet started.

The earlier provisioning audit reported hardware virtualization/SLAT as unavailable and therefore classified BIOS virtualization as a blocker. After the operator enabled virtualization in BIOS/UEFI and rebooted, a follow-up audit produced a contradictory state: `VirtualizationFirmwareEnabled = False`, SLAT = False and VM monitor extensions = False, while `HypervisorPresent = True`.

A dedicated read-only diagnostic on 2026-08-18 resolved that conflict. Windows reports `HypervisorPresent = True` and `Win32_DeviceGuard.VirtualizationBasedSecurityStatus = 2`, which establishes that the Windows VBS/VSM hypervisor layer is active. Memory Integrity/HVCI is disabled and Credential Guard was not detected. Therefore the earlier processor-WMI negatives are not accepted as proof that BIOS virtualization is disabled. The BIOS virtualization gate is **PRESUMED PASS / HYPERVISOR ACTIVE**.

Controlled Oracle VirtualBox provisioning then passed on 2026-08-18. Exact Oracle VirtualBox `7.2.14` revision `174565` was acquired; installer SHA-256 `5fb111f32a15763d519bf9ef23e0111153521f641cde7460e5b8e895ca27a1d2` matched Oracle SHA256SUMS and Authenticode verification passed. The base platform was installed without Extension Pack. `VBoxManage` is operational. Dedicated VM `ARVECTUM-P0-2-RECOVERY` was created as `Windows11_64` with 4096 MB RAM, 2 vCPU, EFI and no network adapter. The VM engine started successfully, a running state was observed, the VM was powered off afterward, and hypervisor-level network disconnect capability (`nic1=none`) was proven. VBS/security controls were not deliberately disabled.

Evidence: `docs/evidence/P0_2_VIRTUALBOX_PROVISIONING_EVIDENCE.json`.

## Recorded host observations

### Initial provisioning audit — 2026-08-17

- reported Windows edition: `Windows 10 Home`;
- reported build family: `26200`;
- architecture: x64;
- RAM: 8 GB;
- free VM storage: 95 GB;
- hardware virtualization reported: **NO**;
- SLAT reported: **NO**;
- Windows Sandbox: **NO**;
- Hyper-V: `HYPER_V_NOT_AVAILABLE`;
- Hyper-V management cmdlets: **NO**;
- VirtualBox: not installed at that time;
- VMware: not installed;
- QEMU: not installed;
- Windows install media: not found;
- dedicated VM `ARVECTUM-P0-2-RECOVERY`: not created at that time.

Initial evidence: `docs/evidence/P0_2_HARDWARE_VIRTUALIZATION_BLOCKER.json`.

### Post-BIOS re-verification — 2026-08-18

After the human operator enabled virtualization in BIOS/UEFI and rebooted:

- `VirtualizationFirmwareEnabled`: **False**;
- `SecondLevelAddressTranslationExtensions`: **False**;
- `VMMonitorModeExtensions`: **False**;
- `HypervisorPresent`: **True**;
- Windows Sandbox: `NOT_AVAILABLE`;
- Hyper-V: `NOT_AVAILABLE`;
- selected provisional third-party path: VirtualBox.

This was recorded as a diagnostic conflict rather than a proven hardware-virtualization failure.

Evidence: `docs/evidence/P0_2_VIRTUALIZATION_DIAGNOSTIC_CONFLICT.json`.

### Diagnostic resolution — 2026-08-18

Read-only follow-up evidence:

- `HypervisorPresent`: **YES**;
- `systeminfo` explicit hypervisor detection line: **UNKNOWN**;
- VBS/VSM status code: `2`;
- VBS/VSM classification: **RUNNING**;
- Device Guard `SecurityServicesConfigured`: `0`;
- Device Guard `SecurityServicesRunning`: `0`;
- `hypervisorlaunchtype`: `NOT_EXPLICITLY_SET`;
- Memory Integrity/HVCI: **DISABLED**;
- Credential Guard: **NOT_DETECTED**;
- processor WMI virtualization/SLAT/VM-monitor flags remain false;
- diagnosis: `WINDOWS_VBS_HYPERVISOR_ACTIVE`;
- BIOS virtualization gate: **PRESUMED_PASS**;
- VirtualBox next step: **SAFE_TO_PROVISION**.

Evidence: `docs/evidence/P0_2_VIRTUALIZATION_DIAGNOSTIC_RESOLUTION.json`.

### VirtualBox provisioning + x64 VM-engine smoke — 2026-08-18

- VirtualBox version: `7.2.14` revision `174565`;
- installer: `VirtualBox-7.2.14-174565-Win.exe`;
- installer SHA-256: `5fb111f32a15763d519bf9ef23e0111153521f641cde7460e5b8e895ca27a1d2`;
- Oracle SHA256SUMS match: **YES**;
- Authenticode: **PASS**;
- base VirtualBox installed: **YES**;
- Extension Pack installed: **NO**;
- `VBoxManage` operational: **YES**;
- dedicated VM: `ARVECTUM-P0-2-RECOVERY`;
- guest type: `Windows11_64`;
- RAM: `4096 MB`;
- vCPU: `2`;
- firmware: `EFI`;
- VM network adapter: **NONE**;
- VM engine start: **PASS**;
- running state observed: **YES**;
- final poweroff: **PASS**;
- hypervisor-level network disconnect capability: **PASS**;
- VBS/security controls deliberately disabled: **NO**.

Evidence: `docs/evidence/P0_2_VIRTUALBOX_PROVISIONING_EVIDENCE.json`.

### Windows 11 x64 clean baseline — 2026-08-18

The guest clean-baseline gate passed from the operator completion report.

- ISO: `Windows11_Ent_Eval_25H2_en-us_x64_v2.iso`;
- ISO bytes: `7092807680`;
- local SHA-256: `A61ADEAB895EF5A4DB436E0A7011C92A2FF17BB0357F58B13BBC4062E535E7B9`;
- Microsoft-published SHA-256: same value;
- official hash match: **YES**;
- installed edition: Windows 11 Enterprise Evaluation;
- version: `25H2`;
- build: `26200 (svc_refresh)`;
- guest architecture: x64;
- installation: clean unattended install;
- public networking ever enabled: **NO**;
- VM NIC before/after install: **NONE**;
- product source introduced before snapshot: **NO**;
- P0.1 archive introduced before snapshot: **NO**;
- project build dependencies introduced before snapshot: **NO**;
- guest shutdown before snapshot: **PASS**;
- clean snapshot: `P0-2-CLEAN-BASELINE`;
- snapshot UUID: `e5abd145-780c-457c-8b8c-a4aa01581716`;
- snapshot verified: **YES**;
- portable recovery started: **NO**;
- installer recovery started: **NO**.

Evidence: `docs/evidence/P0_2_CLEAN_BASELINE_EVIDENCE.json`.

The reported host product-name/build combination should be treated as execution-report identity rather than a trusted marketing-name assertion; edition/build reconciliation is secondary to the actual virtualization capability evidence.

## Immediate provisioning boundary

The clean guest/snapshot boundary is closed. The next local sub-gate is **stage controlled recovery inputs into clean VM**:

1. start from the verified `P0-2-CLEAN-BASELINE` recovery state and keep VirtualBox networking disabled;
2. stage the exact frozen GitVerse recovery source at commit `678efda6df68c93db8474c810abd73bca72735b2` from host path `C:\P0_2_STAGE\gitverse-source` using a host-local/offline transport;
3. stage the exact governed P0.1 archive from `C:\P0_2_STAGE\controlled-inputs`, archive bytes `30,996,168`, SHA-256 `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`;
4. inside the guest verify the frozen source identity and archive identity before installing or building anything;
5. confirm VM NIC remains `NONE` and public dependency/source endpoints remain unavailable;
6. only after staging evidence passes, begin the governed endpoint-denied portable recovery proof using CPython `3.12.10` and the exact eight-wheel hash-locked wheelhouse from P0.1;
7. do not claim P0.2 closed even if portable recovery passes while exact Inno Setup `6.7.1` remains uncontrolled/unavailable.

Do not install the Oracle Extension Pack unless required. The base VirtualBox platform package is sufficient for the P0.2 VM and avoids an unnecessary additional license/dependency boundary.

## Required environment properties

- Windows x64, disposable/resettable to verified snapshot `P0-2-CLEAN-BASELINE`;
- independent from the normal developer OS for the actual recovery build;
- receives the exact GitVerse recovery source at commit `678efda6df68c93db8474c810abd73bca72735b2` before build execution;
- receives the exact P0.1 controlled archive (30,996,168 bytes; SHA-256 `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`) through local/offline transport;
- network/public endpoints remain positively disabled for the governed verification/install/build phase;
- CPython `3.12.10` x64 is installed only from the P0.1 archive;
- the exact eight-wheel hash-locked wheelhouse is the sole Python build-package source;
- recovery outputs/evidence can be exported after the build without enabling public dependency acquisition.

## Acceptable implementations

- Windows Sandbox, if available on a suitable host;
- clean Hyper-V Windows x64 VM;
- clean VMware/VirtualBox/other locally controlled Windows x64 VM;
- equivalent owner-controlled disposable Windows x64 recovery host that can be reset/snapshotted and have networking denied.

A normal developer workstation session is not accepted as a substitute for the disposable-host proof.

## Separate installer blocker

Exact Inno Setup `6.7.1` is still not pre-staged. Even after portable recovery passes, P0.2 remains open until that exact installer toolchain is acquired, verified, archived under Arvectum control, and used in an endpoint-denied installer recovery build.
