# P0.2 — disposable Windows x64 recovery environment provisioning

Status: **REQUIRED / LOCAL-INFRASTRUCTURE BLOCKER**.

The endpoint-denied portable recovery proof cannot start on the current execution host. The first attempt established that Windows Sandbox is unavailable/managed and no pre-existing clean/disposable Windows x64 VM exists. The follow-up provisioning audit then found a stronger host-level blocker: hardware virtualization and SLAT were reported unavailable/disabled, Hyper-V is unavailable on the reported Home edition, no third-party hypervisor is installed, and no Windows installation ISO is staged.

This is not a portable-build failure. P0.2 remains open and the next boundary is to enable/prove hardware virtualization in BIOS/UEFI, then provision a controlled disposable Windows x64 VM without weakening the existing endpoint-denial acceptance contract.

## Recorded host observations — 2026-08-17

- reported Windows edition: `Windows 10 Home`;
- reported build family: `26200`;
- architecture: x64;
- RAM: 8 GB;
- free VM storage: 95 GB;
- hardware virtualization: **NO**;
- SLAT: **NO**;
- Windows Sandbox: **NO**;
- Hyper-V: `HYPER_V_NOT_AVAILABLE`;
- Hyper-V management cmdlets: **NO**;
- VirtualBox: not installed;
- VMware: not installed;
- QEMU: not installed;
- Windows install media: not found;
- dedicated VM `ARVECTUM-P0-2-RECOVERY`: not created.

Evidence: `docs/evidence/P0_2_HARDWARE_VIRTUALIZATION_BLOCKER.json`.

The reported product-name/build combination should be treated as an execution-report identity rather than a release-family assertion; the P0.2 gate depends on the actual virtualization capabilities, not the marketing name returned by a particular Windows inventory API.

## Immediate human boundary

1. Enter the host BIOS/UEFI and enable Intel Virtualization Technology / VT-x, or AMD-V / SVM Mode as appropriate for the CPU/firmware.
2. Reboot Windows.
3. Verify from Windows that firmware virtualization is enabled before installing any hypervisor.
4. Only after that proof, provision a local x64 hypervisor suitable for a clean/resettable VM. On a Home edition where Client Hyper-V is unavailable, a third-party path such as Oracle VirtualBox is acceptable if the exact installed version is recorded and the VM network adapter can be positively disconnected for the governed build phase.
5. Stage verified Windows x64 installation media and create the dedicated `ARVECTUM-P0-2-RECOVERY` VM with a clean baseline snapshot/checkpoint.

Do not install a hypervisor before the virtualization re-check passes; if the CPU/firmware genuinely cannot expose the required hardware virtualization, this Windows host is not suitable for P0.2 and another controlled x64 host must be used.

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
