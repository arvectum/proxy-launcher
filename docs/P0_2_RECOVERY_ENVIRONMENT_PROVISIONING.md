# P0.2 — disposable Windows x64 recovery environment provisioning

Status: **REQUIRED / LOCAL-INFRASTRUCTURE BLOCKER**.

The endpoint-denied portable recovery proof cannot start on the current execution host because Windows Sandbox is unavailable/managed and no pre-existing clean/disposable Windows x64 VM is available. The recorded blocker is `NO_DISPOSABLE_WINDOWS_RECOVERY_ENVIRONMENT`.

This is not a portable-build failure. P0.2 remains open and the next boundary is to provision a disposable Windows x64 environment without weakening the existing acceptance contract.

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
