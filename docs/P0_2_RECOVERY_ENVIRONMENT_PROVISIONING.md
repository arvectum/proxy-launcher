# P0.2 — disposable Windows x64 recovery environment provisioning

Status: **REQUIRED / VIRTUALBOX PROVISIONING READY**.

The endpoint-denied portable recovery proof still cannot start because no disposable Windows x64 recovery environment exists. Windows Sandbox is unavailable and no pre-existing clean VM is present.

The earlier provisioning audit reported hardware virtualization/SLAT as unavailable and therefore classified BIOS virtualization as a blocker. After the operator enabled virtualization in BIOS/UEFI and rebooted, a follow-up audit produced a contradictory state: `VirtualizationFirmwareEnabled = False`, SLAT = False and VM monitor extensions = False, while `HypervisorPresent = True`.

A dedicated read-only diagnostic on 2026-08-18 resolved that conflict. Windows reports `HypervisorPresent = True` and `Win32_DeviceGuard.VirtualizationBasedSecurityStatus = 2`, which establishes that the Windows VBS/VSM hypervisor layer is active. Memory Integrity/HVCI is disabled and Credential Guard was not detected. Therefore the earlier processor-WMI negatives are not accepted as proof that BIOS virtualization is disabled. The BIOS virtualization gate is now **PRESUMED PASS / HYPERVISOR ACTIVE**.

The next boundary is controlled VirtualBox provisioning. Do not return to BIOS and do not disable VBS/Memory Integrity/Credential Guard merely to improve virtualization performance. Oracle VirtualBox may use the Windows hypervisor path when Hyper-V/VBS is active; any performance degradation is acceptable for this one-shot recovery proof provided correctness, isolation and endpoint denial are preserved.

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
- VirtualBox / VMware / QEMU: not installed;
- Windows install media: not found;
- dedicated VM `ARVECTUM-P0-2-RECOVERY`: not created.

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

The reported product-name/build combination should be treated as execution-report identity rather than a trusted marketing-name assertion; edition/build reconciliation is secondary to the actual virtualization capability evidence.

## Immediate provisioning boundary

1. acquire the current supported Oracle VirtualBox Windows-host installer from Oracle-controlled distribution;
2. verify the installer against Oracle-published SHA-256 metadata and record exact version/hash before installation;
3. install VirtualBox without Extension Pack unless a later requirement proves it necessary;
4. verify `VBoxManage` is available and record the installed VirtualBox version;
5. acquire verified Windows 11 x64 installation media suitable for an ephemeral recovery VM; a Microsoft 90-day Windows 11 Enterprise evaluation ISO is acceptable because no product key is required for the recovery drill;
6. verify and record the Windows ISO SHA-256 against Microsoft-published hash evidence where available;
7. create dedicated VM `ARVECTUM-P0-2-RECOVERY` using approximately 4 GB RAM, 2 vCPU and a 64 GB dynamically allocated disk on this 8 GB host;
8. install Windows x64, then create a clean baseline snapshot named `P0-2-CLEAN-BASELINE` before product inputs are introduced;
9. prove the VM network adapter can be fully disconnected at the VirtualBox layer;
10. only after the clean VM is ready, stage the exact GitVerse recovery source and P0.1 controlled archive and rerun the endpoint-denied portable recovery proof.

Do not install the Oracle Extension Pack unless required. The base VirtualBox platform package is sufficient for the P0.2 VM and avoids introducing an unnecessary additional license/dependency boundary.

## Required environment properties

- Windows x64, disposable or resettable to a known-clean snapshot;
- independent from the normal developer OS for the actual recovery build;
- able to receive the exact GitVerse recovery source at commit `678efda6df68c93db8474c810abd73bca72735b2` before endpoint denial;
- able to receive the exact P0.1 controlled archive (30,996,168 bytes; SHA-256 `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`) before endpoint denial;
- network/public endpoints can be positively disabled for the entire governed verification/install/build phase;
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

Exact Inno Setup `6.7.1` is also not yet pre-staged. Even after portable recovery passes, P0.2 remains open until that exact installer toolchain is acquired, verified, archived under Arvectum control, and used in an endpoint-denied installer recovery build.
