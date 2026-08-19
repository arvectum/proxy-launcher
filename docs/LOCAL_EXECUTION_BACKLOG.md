# Arvectum Proxy Launcher — remaining local / human / infrastructure backlog

Updated: 2026-08-19

This file contains work that cannot be truthfully completed by hosted repository automation alone. The protected customer-proven Windows `0.2.3` system-proxy baseline must remain unchanged while these items are executed.

## P0 — Windows production release contour

### P0.1 Controlled Windows build inputs — DONE

Status: **DONE / CLOSED 2026-08-17**.

Canonical governed archive:

- archive: `arvectum-windows-build-inputs-cpython-3.12.10-x64.zip`;
- bytes: `30996168`;
- SHA-256: `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`;
- CPython: `3.12.10` x64, governed installer identity verified;
- wheelhouse: exactly eight approved Windows x64 wheels;
- wheelhouse hash-lock SHA-256: `6587ee8cc6e7528f3d86dcfcca16fb731b48102a7a24fc6f0f12363f79020943`;
- canonical evidence: `docs/evidence/P0_1_COMPLETION_EVIDENCE.json`;
- canonical storage profile: `docs/P0_1_CONTROLLED_STORAGE_PROFILE.md`.

The controlled archive has been retained under Arvectum control and an independent offline copy was previously byte-matched and physically separated. P0.1 is sufficient to preserve the key governed Windows build dependencies for a later independent rebuild drill.

### P0.2 Independent clean-machine endpoint-denied rebuild drill — DEFERRED

Status: **DEFERRED / NOT RELEASE BLOCKER**.

Purpose:

- prove future disaster-recovery/reproducibility from a clean Windows environment;
- use only the frozen source authority plus governed P0.1 CPython/wheelhouse inputs;
- deny public package/source endpoints during the entire rebuild;
- run full tests, package-contract/branding checks, SBOM/dependency coverage and artifact comparison.

Why deferred:

- a customer-proven sealed Windows `0.2.3` artifact already exists;
- P0.1 has already preserved the critical controlled Windows build inputs;
- the clean-machine drill is resilience/supply-chain assurance rather than a prerequisite for the current production release;
- the attempted VirtualBox path encountered host-specific VBS/NEM/EFI/SMP incompatibilities, and the project will not weaken Windows security controls or bypass Windows 11 requirements just to satisfy a recovery-environment implementation detail.

Historical/forensic evidence from the attempted VirtualBox path remains valid only for what it actually proves. In particular, the original `P0-2-CLEAN-BASELINE` must not be treated as a successful restore/cold-boot baseline after later diagnostic failure.

Future execution policy:

1. wait until a suitable clean Windows machine/environment is naturally available;
2. do not require any specific hypervisor — the drill is hypervisor-independent;
3. verify the clean environment itself before staging product inputs;
4. use the governed P0.1 archive as the sole CPython/wheelhouse source;
5. verify source identity at the chosen frozen recovery authority;
6. prove endpoint denial before and after build;
7. run the canonical portable and, if desired, installer rebuild without live acquisition;
8. export non-secret evidence, SBOM and hashes;
9. compare product contract/artifacts against the governed candidate and document expected nondeterminism.

This task remains in backlog until convenient infrastructure exists. It must not block Windows installer/signing/release work.

### P0.3 Inno Setup 6.7.1 controlled acquisition + production installer — ACTIVE

Repository/autonomous preparation is complete via merged PR #92, historically named `[Win] P0.2-B — Inno Setup 6.7.1 sovereignty preparation`.

Exact compiler authority is frozen in:

`tools/inno-setup-windows.lock`

Current locked identity includes:

- Inno Setup version: `6.7.1`;
- release tag: `is-6_7_1`;
- installer: `innosetup-6.7.1.exe`;
- expected bytes: `10619024`;
- expected SHA-256: `4d11e8050b6185e0d49bd9e8cc661a7a59f44959a621d31d11033124c4e8a7b0`;
- required Authenticode publisher: `Pyrsys B.V.`;
- detached vendor signature/public-key/license inputs are part of the controlled bundle contract.

Repository tooling already present:

- connected acquisition/verifier: `tools/prepare_windows_inno_setup_base.ps1`;
- offline verified installation helper: `tools/install_verified_windows_inno_setup.ps1`;
- installer builder: `tools/build_windows_installer.ps1`;
- contract tests: `tests/test_windows_inno_setup_sovereignty.py`;
- canonical installer definition rejects compiler versions other than exact `6.7.1`.

Required local boundary now:

1. on a connected Windows host, run the canonical acquisition/verifier and obtain the exact controlled bundle;
2. require exact size/SHA-256 plus valid Authenticode publisher according to the repository lock;
3. retain the verified bundle under Arvectum control;
4. run the canonical Windows production installer build with exact `ISCC.exe 6.7.1`;
5. verify generated installer metadata/hash and real install/update/uninstall/rollback behavior;
6. preserve non-secret build/release evidence.

The former `BLOCKED_MISSING_PRESTAGED_INNO_6_7_1` remains relevant only if/when the deferred endpoint-denied recovery drill is resumed. For the current production release, connected controlled acquisition is allowed and is the active path.

### P0.4 Russian-first Windows signing + final release package

Start after the production installer is built and accepted.

Required local/hardware/external boundary:

- Russian-first production signing using the approved КриптоПро / Рутокен / Russian trust contour;
- canonical portable + installer release package;
- SHA-256/release evidence/SBOM/notices as applicable;
- real Windows install/update/uninstall/rollback acceptance;
- final retained artifact/source/build identity.

International Microsoft/GlobalSign-oriented signing remains lower priority and is not a release blocker for the Russian-first product line.

## P1 — APL-LNX-010 real Astra Linux acceptance + Gate R8

Required local boundary: a real supported Astra Linux graphical host/session.

Start with:

```bash
bash qa/collect_astra_acceptance_preflight.sh
```

Then execute the real `.deb` acceptance matrix, including install/start/GUI, runtime/backend detection, NetworkManager preflight, enable/sync/disable and rollback, autostart/session behavior, crash/restart/reboot recovery, uninstall/update and diagnostics privacy review.

Gate R8 closes only from real-host evidence.

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
- shipped artifacts reconciled with SBOM/licenses/notices;
- chain-of-title evidence verified;
- decision is **APPROVED**;
- only then create the clean IP baseline/tag.

Automation must not mark this complete on behalf of a human reviewer.

## P3 — APL-ROUTE-003 Windows per-application routing product decision

Production WFP connect-redirection requires a native/kernel enforcement decision and Windows kernel-signing/distribution path. Choose deliberately:

1. accept Microsoft Hardware Dev Center + accepted EV identity dependency for an optional per-app Windows SKU;
2. adopt a separately reviewed already-signed third-party component;
3. prove a supported user-mode architecture with equivalent semantics;
4. defer Windows per-app routing and keep system-proxy/domain/IP functionality as the production line.

Do not use test-signing/developer mode as a production workaround.

## P4 — macOS real acceptance / Gate R9 — DONE

Closed from real Mac acceptance evidence on 2026-08-17.

## P5 — controlled Linux/macOS build-input mirrors

Status: **DEFERRED / MEDIUM PRIORITY**.

When useful:

- archive/mirror pinned Python/build inputs required by Linux/macOS packaging;
- archive exact AppImage build/runtime inputs;
- add immutable hashes/recovery instructions;
- run at least one public-endpoint-denied build.

## Deferred feature work

- Astra per-application routing prototype: after Windows routing policy is settled and a real privileged Astra test host is available.
- macOS per-application routing: after entitlement/distribution-model proof for NetworkExtension/managed per-app routing.
- international Apple/Microsoft signing/notarization paths: lower priority than the Russian-first release contour.

## Current execution order

1. **P0.3 — Inno Setup 6.7.1 controlled acquisition + production installer.**
2. **P0.4 — Russian-first Windows signing + final release package.**
3. **P1 — real Astra Linux acceptance / Gate R8.**
4. **P2 — APL-IP-001 human/legal sign-off.**
5. **P3 — Windows per-app routing product decision.**
6. Deferred resilience/hardening tasks when infrastructure or product need makes them worthwhile.

## Completion discipline

Do not relabel real-host, signing, external-platform or human/legal gates as complete from mocks, CI or documentation. Conversely, do not allow deferred resilience work to block an already customer-proven production line unless a new explicit risk decision promotes it back onto the critical path.
