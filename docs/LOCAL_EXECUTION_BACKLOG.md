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

Status: **IN PROGRESS — CLEAN BASELINE PASS / CONTROLLED INPUT STAGING NEXT / INSTALLER TOOLCHAIN BLOCKED**.

Completed preflight and recovery-environment sub-gates:

- canonical recovery target commit: `678efda6df68c93db8474c810abd73bca72735b2`;
- fresh source recovery from GitVerse: **PASS**;
- fresh recovery checkout path at execution: `C:\P0_2_STAGE\gitverse-source`;
- exact GitVerse commit match: **YES**;
- governed P0.1 archive staged on host at `C:\P0_2_STAGE\controlled-inputs`;
- archive bytes: `30996168`;
- archive SHA-256: `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`;
- `tools/verify_windows_build_input_archive.ps1 -RequireCurrentRepositoryLocks`: **PASS**;
- exact Inno Setup `6.7.1` / `ISCC.exe` pre-staged: **NO**;
- installer recovery status: **BLOCKED_MISSING_PRESTAGED_INNO_6_7_1**;
- non-secret preflight evidence: `docs/evidence/P0_2_PREFLIGHT_EVIDENCE.json`;
- read-only virtualization resolution diagnosed `WINDOWS_VBS_HYPERVISOR_ACTIVE`; BIOS virtualization gate **PRESUMED_PASS / HYPERVISOR ACTIVE**; no Windows security controls were deliberately disabled;
- Oracle VirtualBox `7.2.14` revision `174565` controlled and installed without Extension Pack;
- VirtualBox installer SHA-256 `5fb111f32a15763d519bf9ef23e0111153521f641cde7460e5b8e895ca27a1d2` matched Oracle SHA256SUMS; Authenticode **PASS**;
- dedicated VM `ARVECTUM-P0-2-RECOVERY`: **CREATED**;
- VM configuration: 4096 MB RAM, 2 vCPU, EFI, 64 GB dynamic disk, NIC `NONE`;
- x64 VM-engine smoke: **PASS**;
- hypervisor-level network disconnect capability: **PASS**;
- evidence: `docs/evidence/P0_2_VIRTUALBOX_PROVISIONING_EVIDENCE.json`.

Clean Windows guest baseline — **PASS 2026-08-18**:

- official Microsoft Windows 11 Enterprise Evaluation 25H2 x64 en-US ISO: `Windows11_Ent_Eval_25H2_en-us_x64_v2.iso`;
- ISO bytes: `7092807680`;
- local SHA-256: `A61ADEAB895EF5A4DB436E0A7011C92A2FF17BB0357F58B13BBC4062E535E7B9`;
- Microsoft-published SHA-256: same value;
- official hash match: **YES**;
- guest install: clean unattended Windows 11 Enterprise Evaluation 25H2 x64;
- guest build: `26200 (svc_refresh)`;
- public networking ever enabled during install/OOBE: **NO**;
- VM NIC before/after install: **NONE**;
- product source introduced before snapshot: **NO**;
- P0.1 archive introduced before snapshot: **NO**;
- project build dependencies introduced before snapshot: **NO**;
- guest shutdown before snapshot: **PASS**;
- snapshot: `P0-2-CLEAN-BASELINE`;
- snapshot UUID: `e5abd145-780c-457c-8b8c-a4aa01581716`;
- snapshot verified: **YES**;
- portable recovery started: **NO**;
- installer recovery started: **NO**;
- evidence: `docs/evidence/P0_2_CLEAN_BASELINE_EVIDENCE.json`.

Required local/infrastructure boundary now:

1. start from the verified `P0-2-CLEAN-BASELINE` state and keep VM networking disabled at hypervisor level;
2. transfer the exact frozen GitVerse recovery checkout from host path `C:\P0_2_STAGE\gitverse-source` into the guest using local/offline transport; do not fetch from GitHub/GitVerse inside the guest;
3. transfer the exact governed P0.1 archive from `C:\P0_2_STAGE\controlled-inputs` into the guest using local/offline transport;
4. verify inside the guest that source authority is exact commit `678efda6df68c93db8474c810abd73bca72735b2` and that the P0.1 archive is exactly `30996168` bytes / SHA-256 `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`;
5. confirm VM NIC remains `NONE` and public endpoints are unavailable before any dependency installation/build activity;
6. run the canonical P0.1 archive verifier inside the guest and install CPython `3.12.10` x64 only from the governed archive;
7. use only the exact eight-wheel hash-locked wheelhouse with `PIP_NO_INDEX=1` / offline-hash-locked mode;
8. run the endpoint-denied portable recovery proof, tests, package-contract/branding checks, deterministic offline recovery SBOM and locked dependency coverage;
9. verify endpoint denial before and after build and export non-secret evidence to host without enabling public acquisition;
10. compare resulting artifact/product contract and classify any expected binary nondeterminism;
11. separately bring exact Inno Setup `6.7.1` under Arvectum-controlled/pre-staged storage and prove endpoint-denied installer recovery before P0.2 can close.

Acceptance:

- clean/disposable Windows x64 recovery host is proven through `P0-2-CLEAN-BASELINE`;
- source recovery comes from GitVerse at the exact governed commit rather than GitHub;
- public package/source endpoints remain denied during actual controlled install/build;
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
