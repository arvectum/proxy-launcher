# Arvectum Proxy Launcher — remaining local / human / infrastructure backlog

Updated: 2026-08-18

This file contains only work that cannot be truthfully completed by hosted repository automation alone. The protected Windows `0.2.3` system-proxy baseline must remain unchanged while these items are executed.

## P0 — Windows sovereign-build infrastructure closure

**Why first:** release recoverability and dependency sovereignty are higher risk than adding new features.

### P0.1 Archive controlled build inputs — DONE

Status: **DONE / CLOSED 2026-08-17**.

Final governed archive:

- archive: `arvectum-windows-build-inputs-cpython-3.12.10-x64.zip`;
- archive bytes: `30996168`;
- archive SHA-256: `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`;
- CPython installer: `python-3.12.10-amd64.exe`, SHA-256 `67b5635e80ea51072b87941312d00ec8927c4db9ba18938f7ad2d27b328b95fb`, Sigstore offline-bundle identity verification **PASS**;
- wheelhouse target: CPython `3.12.10`, `win_amd64`, implementation `cp`, ABI `cp312`, exactly eight governed wheels, hash-lock SHA-256 `6587ee8cc6e7528f3d86dcfcca16fb731b48102a7a24fc6f0f12363f79020943`.

Closed acceptance evidence:

- local archive verifier: **PASS**;
- primary controlled storage: Arvectum-controlled Mac mini, exact ZIP/sidecar/evidence byte-match with Windows source **YES**;
- primary three source artifacts read-only + `uchg`: **YES**;
- primary directory world-writable: **NO**;
- access policy recorded: **YES**;
- retention policy recorded: **YES**;
- independent removable offline copy: `ARVECTUM-1`, `exFAT`, `16.0 GB`;
- ZIP/sidecar/evidence byte-match primary: **YES**;
- macOS `sync` + software eject: **PASS**;
- physical disconnect from primary host: **YES**;
- final Windows offline-copy canonical verifier with current repository locks and package-index access disabled: **PASS** at commit `1429e55959e9a3940b1f2e03e84f18fa7b05de0c`;
- fresh Windows retrieval of Mac mini primary copy canonical verifier: **PASS**;
- primary/offline ZIP, sidecar and evidence byte-match after round trip: **YES**;
- final Windows safe eject and physical disconnect: **YES, human confirmed**;
- offline device returned to separate storage: **YES**;
- final non-secret evidence: `docs/evidence/P0_1_COMPLETION_EVIDENCE.json`;
- secrets in evidence: **NO**.

P0.1 acceptance is fully satisfied. The governed archive can now be used as the sole CPython/wheelhouse source for P0.2.

### P0.2 Independent endpoint-denied recovery build

Status: **IN PROGRESS — PREFLIGHT PASS / VIRTUALBOX PROVISIONING READY / INSTALLER TOOLCHAIN BLOCKED**.

Completed preflight sub-gate:

- canonical recovery target commit: `678efda6df68c93db8474c810abd73bca72735b2`;
- fresh source recovery from GitVerse: **PASS**;
- fresh recovery checkout path at execution: `C:\P0_2_STAGE\gitverse-source`;
- exact GitVerse commit match: **YES**;
- governed P0.1 archive staged at `C:\P0_2_STAGE\controlled-inputs`;
- archive bytes: `30996168`;
- archive SHA-256: `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`;
- `tools/verify_windows_build_input_archive.ps1 -RequireCurrentRepositoryLocks`: **PASS**;
- exact Inno Setup `6.7.1` / `ISCC.exe` found in standard locations or PATH: **NO**;
- installer recovery status: **BLOCKED_MISSING_PRESTAGED_INNO_6_7_1**;
- non-secret preflight evidence: `docs/evidence/P0_2_PREFLIGHT_EVIDENCE.json`.

Recovery-environment evidence:

- Windows Sandbox unavailable on the current host;
- no pre-existing clean/disposable Windows x64 VM;
- reported host edition/build identity: `Windows 10 Home` / `25H2` / build `26200`; this inventory name is treated as execution-report identity rather than a trusted marketing-name assertion;
- host architecture: x64; RAM: 8 GB; free VM storage: 95 GB;
- initial processor WMI virtualization/SLAT/VM-monitor flags reported **NO**;
- after the operator enabled virtualization in BIOS/UEFI and rebooted, Windows reported `HypervisorPresent = YES` while the processor WMI flags remained false;
- read-only resolution diagnostic: `Win32_DeviceGuard.VirtualizationBasedSecurityStatus = 2`, classification **VBS/VSM RUNNING**;
- Memory Integrity/HVCI: **DISABLED**; Credential Guard: **NOT_DETECTED**;
- diagnosis: `WINDOWS_VBS_HYPERVISOR_ACTIVE`;
- BIOS virtualization gate: **PRESUMED_PASS / HYPERVISOR ACTIVE**;
- Windows Sandbox / Client Hyper-V are not available as the chosen recovery path;
- VirtualBox / VMware / QEMU are not currently installed;
- VirtualBox next step: **SAFE_TO_PROVISION** without disabling Windows security controls;
- dedicated recovery VM `ARVECTUM-P0-2-RECOVERY`: not yet created;
- evidence: `docs/evidence/P0_2_VIRTUALIZATION_DIAGNOSTIC_RESOLUTION.json`;
- provisioning contract: `docs/P0_2_RECOVERY_ENVIRONMENT_PROVISIONING.md`.

Required local/infrastructure boundary now:

1. acquire the current supported Oracle VirtualBox Windows-host installer from Oracle-controlled distribution and verify its Oracle-published SHA-256 before installation;
2. install base VirtualBox only; do not add the Extension Pack unless a later requirement proves it necessary;
3. acquire verified Windows 11 x64 installation media suitable for an ephemeral recovery VM; Microsoft Windows 11 Enterprise evaluation ISO is acceptable;
4. create `ARVECTUM-P0-2-RECOVERY` with approximately 4 GB RAM, 2 vCPU and a 64 GB dynamically allocated disk on this 8 GB host;
5. install the guest OS and create clean snapshot `P0-2-CLEAN-BASELINE` before product inputs are introduced;
6. prove the VirtualBox network adapter can be fully disconnected at hypervisor level;
7. stage the exact GitVerse recovery checkout and P0.1 controlled archive into the clean VM before endpoint denial;
8. run the endpoint-denied portable recovery proof using governed CPython `3.12.10` and the exact eight-wheel hash-locked wheelhouse;
9. generate endpoint-denial evidence, build-result evidence and offline recovery SBOM without live package acquisition;
10. compare resulting artifact/product contract and classify any binary differences;
11. separately bring exact Inno Setup `6.7.1` under controlled/pre-staged storage and prove installer recovery before P0.2 can close.

Acceptance:

- clean/disposable Windows x64 recovery host is proven;
- source recovery comes from GitVerse at the exact governed commit rather than GitHub;
- public package/source endpoints remain denied during the actual install/build phase;
- controlled P0.1 archive remains the sole CPython/wheelhouse input;
- canonical portable build succeeds in `offline-hash-locked` mode;
- exact Inno Setup `6.7.1` is controlled/pre-staged and the canonical installer build succeeds without live acquisition;
- release evidence and offline recovery SBOM are produced;
- hashes/diffs are compared against the canonical candidate and any expected nondeterminism is documented;
- no unexplained artifact/product-contract difference remains;
- GitVerse/self-hosted recovery procedure is proven rather than merely documented.

P0.2 must remain open if the portable proof succeeds but Inno Setup `6.7.1` remains unavailable; do not weaken the installer acceptance gate.

## P1 — APL-LNX-010 real Astra Linux acceptance + Gate R8

Required local boundary: a real supported Astra Linux graphical host/session.

Start with the repository collector:

```bash
bash qa/collect_astra_acceptance_preflight.sh
```

Then execute the APL-LNX-010 acceptance matrix on the actual `.deb` candidate, including:

- install/start/GUI;
- runtime/backend detection;
- NetworkManager capability/preflight;
- enable/sync/disable and exact rollback;
- autostart/session behavior;
- crash/restart/reboot recovery;
- uninstall/update and user-state preservation;
- diagnostics/support bundle privacy review.

Gate R8 closes only if real-host evidence passes. Hosted Ubuntu CI is not a substitute.

## P2 — APL-IP-001 authorized human/legal sign-off

Required human/legal boundary: authorized reviewer(s) able to judge authorship, licensing and chain of title for ООО «Арвектум».

Use:

- `docs/APL_IP_001_PROVENANCE_HARDENING.md`;
- `docs/APL_IP_001_HUMAN_LEGAL_SIGNOFF.md`;
- final source provenance manifest;
- final SBOM(s) and third-party notices;
- actual employee/contractor/pre-company/brand-asset rights documents.

Acceptance:

- significant-source review complete;
- all final shipped artifacts reconciled with SBOM/licenses/notices;
- chain-of-title evidence verified;
- decision in the sign-off record is **APPROVED**;
- only then create a clean IP tag pointing to the exact reviewed commit (recommended convention: `ip-clean/<product-version>/<YYYY-MM-DD>`).

Automation must not mark this complete on behalf of a human reviewer.

## P3 — APL-ROUTE-003 Windows per-application routing product decision

Required product/external-platform boundary before further native implementation.

Production WFP connect-redirection requires a kernel/native enforcement path whose normal Windows production loading/signing chain creates an external Microsoft/accepted-EV dependency. Choose one path deliberately:

1. accept that dependency for an optional per-app Windows SKU;
2. adopt a separately reviewed already-signed third-party enforcement component;
3. prove a supported user-mode architecture with equivalent semantics;
4. defer Windows per-app routing and keep the proven system-proxy/domain/IP product as the production line.

Do **not** use test-signing/developer mode as a production workaround.

If path 1 or 2 is chosen, the next local work becomes native install/update/remove ownership, signing, privileged WFP enforcement, loop prevention, crash/reboot rollback and real Windows acceptance.

## P4 — APL-MAC-008 real macOS acceptance + Gate R9 — DONE

Closed from real MacBook acceptance evidence on 2026-08-17.

## P5 — controlled Linux/macOS build-input mirrors

Required infrastructure boundary: Russian/Arvectum-controlled artifact/mirror storage and the corresponding build-host routing/credentials.

Scope after P0:

- archive/mirror pinned Python/build inputs required by Linux and macOS packaging;
- archive the exact AppImage build/runtime inputs used by the release process;
- add immutable hashes and recovery instructions;
- run at least one build with public package endpoints unavailable.

This is medium priority because Windows is the customer-proven primary platform and should receive sovereignty closure first.

## Deferred feature work after the gates above

- Astra per-application routing prototype: only after the Windows routing policy is settled and a real Astra privileged test host is available; expected direction is controlled cgroup/socket identity plus nftables/policy-routing.
- macOS per-application routing: only after entitlement/distribution-model proof for NetworkExtension/managed per-app routing.
- international Apple/Microsoft signing/notarization paths: remain lower priority than the Russian-first production/release path unless product strategy changes.

## Completion discipline

Do not relabel any item above as complete from mocks, hosted CI, documentation, or synthetic evidence. Close each item only from the named real-host, infrastructure, external-platform, or human/legal evidence boundary.
