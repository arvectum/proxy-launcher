# P0.2 — disposable Windows x64 recovery environment provisioning

Status: **REQUIRED / LOCAL-INFRASTRUCTURE DIAGNOSTIC GATE**.

The endpoint-denied portable recovery proof still cannot start because no disposable Windows x64 recovery environment exists. Windows Sandbox is unavailable and no pre-existing clean VM is present.

The earlier provisioning audit reported hardware virtualization/SLAT as unavailable and therefore classified BIOS virtualization as a blocker. After the operator enabled virtualization in BIOS/UEFI and rebooted, a follow-up audit produced a contradictory state: `VirtualizationFirmwareEnabled = False`, SLAT = False and VM monitor extensions = False, while `HypervisorPresent = True`.

That combination is not sufficient to conclude that BIOS virtualization is still disabled. When a Windows hypervisor/VBS/VSM layer is already running, normal host requirement reporting can be suppressed or altered. The next boundary is therefore a read-only Windows hypervisor/VBS diagnostic, not another BIOS change.

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

This is recorded as a **diagnostic conflict**, not a proven hardware-virtualization failure.

Evidence: `docs/evidence/P0_2_VIRTUALIZATION_DIAGNOSTIC_CONFLICT.json`.

The reported product-name/build combination should also be treated as execution-report identity rather than a trusted marketing-name assertion; edition/build reconciliation is secondary to the actual virtualization capability evidence.

## Immediate diagnostic boundary

Before any additional BIOS change or VirtualBox installation:

1. inspect whether Windows Virtualization-Based Security / Virtual Secure Mode is running;
2. inspect boot configuration (`hypervisorlaunchtype`) and relevant optional Windows virtualization features;
3. capture `msinfo32` hypervisor/VBS state;
4. classify whether the current `HypervisorPresent = True` is explained by Windows VBS/VSM or another active hypervisor layer;
5. only then decide whether VirtualBox can be provisioned as-is or whether a Windows security/hypervisor compatibility decision is required.

Do not disable Memory Integrity, Credential Guard, VBS/VSM, Secure Boot or other security controls merely to make P0.2 pass. Any such change requires a deliberate security trade-off and is not part of this diagnostic gate.

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
