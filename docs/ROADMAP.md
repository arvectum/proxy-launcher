# Arvectum Proxy Launcher — canonical roadmap

Updated: 2026-08-18
Canonical branch: `main`
Current product version: `0.2.3`

Status legend:

- **DONE** — implementation and required automated acceptance are complete.
- **AUTONOMOUS COMPLETE / LOCAL ACCEPTANCE PENDING** — repository/CI work is complete; remaining evidence requires the target machine or privileged local execution.
- **HUMAN/LEGAL PENDING** — engineering controls are complete, but judgment/sign-off cannot be replaced by automation.
- **LOCAL/NATIVE DEBT** — next meaningful step requires a real host, privileged/native component, hardware-backed identity, external infrastructure, or equivalent local boundary.
- **STOP-GATE** — do not continue implementation until the named product/legal/infrastructure decision is made.

## 0. Proven Windows/core baseline

The customer-proven Windows `0.2.3` system-proxy path remains protected. New routing work must not silently replace or destabilize it.

- **DONE** — APL-CORE-007 — unified backend contract & regression matrix.
- **DONE** — Windows portable/customer baseline and release/recovery safeguards already present in `main`.
- **DONE** — Windows runtime/installer/security/diagnostics/productization CI already present in `main`.
- **DONE** — final autonomous sweep merge `449ba8abfb696ef4eaf66c958040a30adbd61111`; post-merge GitHub checks observed without a failing conclusion, including mirror, exact-SHA release evidence, macOS packaging and dependency audit jobs.
- **CONSTRAINT** — per-application routing is a new enforcement plane and remains separated from the proven system-proxy baseline.

## 1. Linux / Astra Linux

- **DONE** — APL-LNX-006 — Linux diagnostics & support bundle.
- **DONE** — APL-LNX-007 — Debian `.deb` packaging (merged independently as PR #66).
- **DONE** — APL-LNX-008 — AppImage packaging with hash-pinned build-only toolchain and extraction acceptance.
- **DONE** — APL-LNX-009 — Ubuntu 22.04/24.04 CI acceptance, including ephemeral dpkg install/remove and user-state preservation.
- **DONE** — APL-IP-002-LNX — Linux stack & dependency sovereignty audit (conditional pass).
- **DONE** — local-work reduction: `qa/collect_astra_acceptance_preflight.sh` collects read-only Astra/NetworkManager/package/session evidence without changing network state.
- **AUTONOMOUS COMPLETE / LOCAL ACCEPTANCE PENDING** — APL-LNX-010 — real Astra Linux graphical/runtime/package acceptance.
- **LOCAL/NATIVE DEBT** — Gate R8 — close only from APL-LNX-010 real-host evidence.

### Linux release policy

For controlled Astra deployments, `.deb` is preferred because it avoids the additional AppImage runtime stub. AppImage remains an optional portable format.

## 2. macOS

- **DONE** — APL-MAC-001 — side-effect-free runtime and read-only `networksetup` preflight.
- **DONE** — APL-MAC-002 — capability/failure UX contract.
- **DONE** — APL-MAC-003 — privacy-bounded diagnostics/support bundle.
- **DONE** — APL-MAC-004 — deterministic `.app` packaging with stable bundle id and arm64/x64 CI.
- **DONE** — APL-MAC-005 — DMG packaging and read-only mount inspection.
- **DONE** — APL-MAC-006 — per-user LaunchAgent ownership/autostart model.
- **DONE** — APL-MAC-007 — packaging/recovery ownership contract tests.
- **DONE** — APL-IP-002-MAC — macOS stack & dependency sovereignty audit (conditional pass).
- **DONE** — integration hardening: macOS preflight is wired into the common backend operational gate before new `enable/sync` mutations; recovery/disable remains reachable.
- **DONE** — local-work reduction: `qa/collect_macos_acceptance_preflight.sh` collects read-only OS/app/DMG/LaunchAgent/rollback-metadata evidence.
- **DONE** — APL-MAC-008 — real macOS GUI/system-proxy/autostart/crash-recovery acceptance.
- **DONE** — Gate R9 — closed from APL-MAC-008 real-host evidence.

Apple production identity signing/notarization is not a functional correctness gate in the current Russian-first release strategy; it remains a later distribution-policy task unless priorities change.

## 3. Cross-platform sovereignty / IP

- **DONE** — APL-IP-002-WIN — Windows stack/dependency sovereignty audit; remediation findings remain binding.
- **DONE** — APL-IP-002-LNX.
- **DONE** — APL-IP-002-MAC.
- **DONE** — APL-IP-002-FINAL — consolidated cross-platform conditional verdict.
- **AUTONOMOUS COMPLETE / HUMAN/LEGAL PENDING** — APL-IP-001 — source provenance/human-authorship hardening.
  - source/build/config inventory + SHA-256 manifest: done;
  - third-party boundary/notices: done;
  - CI evidence: done;
  - human/legal completion record: done (`docs/APL_IP_001_HUMAN_LEGAL_SIGNOFF.md`);
  - human review of significant modules: pending;
  - chain-of-title/legal review for ООО «Арвектум»: pending;
  - clean IP baseline/tag: blocked until those reviews are signed off.

### Windows build-sovereignty remediation — autonomous portion complete

- **DONE (engineering control)** — exact Windows x64 wheel set and SHA-256 hash lock in `requirements-build.windows-x64.hashes.txt`.
- **DONE (engineering control)** — verified wheelhouse acquisition script with exactly eight approved wheels and `wheelhouse-manifest.json`.
- **DONE (engineering control)** — canonical Windows build supports `offline-hash-locked` mode with `PIP_NO_INDEX=1`, `--no-index`, `--only-binary=:all:` and `--require-hashes`.
- **DONE (CI control)** — dedicated Windows workflow acquires/validates the wheelhouse, then rebuilds portable with package-index access disabled.
- **DONE (engineering control)** — exact CPython 3.12.10 x64 bootstrap identity is pinned and verified through Sigstore before installation in the controlled build workflow.
- **DONE (engineering control)** — P0.1 adds a network-free self-contained CPython/wheelhouse archive packager, full-payload SHA-256 manifest and independent offline verifier (`tools/archive_windows_build_inputs.ps1`, `tools/verify_windows_build_input_archive.ps1`).
- **DONE** — build-only `pip` baseline moved from `25.3` to `26.1.2`; frozen PyInstaller/application runtime inputs otherwise unchanged.
- **DONE (P0.1 local acquisition/verification sub-gate)** — governed archive `arvectum-windows-build-inputs-cpython-3.12.10-x64.zip`, `30,996,168` bytes, SHA-256 `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`, passed the canonical offline verifier with current repository locks at commit `60c456aa90ef8c6269ca79fdde9ad5861ebb6398`.
- **DONE (P0.1 primary transfer/byte-match sub-gate)** — the exact ZIP, sidecar and evidence JSON were transferred over authenticated private-LAN SCP to the canonical Arvectum-controlled Mac mini directory; remote size is `30,996,168` bytes, remote SHA-256 is the same `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`, byte-match with the Windows source is **YES**.
- **DONE (P0.1 primary sealing sub-gate)** — the three primary artifacts are read-only and `uchg`, the canonical directory is not world-writable, access/retention policy is recorded, and SHA-256 remained `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886` before/after sealing.
- **DONE (P0.1 removable offline-copy software verification/eject sub-gate)** — the exact three-file governed set was copied to external/removable `ARVECTUM-1` (`exFAT`, `16.0 GB`), ZIP/sidecar/evidence byte-match the primary copy, archive size is `30,996,168`, SHA-256 is `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`, `sync` passed, `diskutil eject` passed and the volume was no longer mounted.
- **DONE (P0.1 physical-disconnection human sub-gate)** — after successful software eject, the human operator physically unplugged `ARVECTUM-1` from the Mac mini on `2026-08-17`.
- **DONE (P0.1 final Windows round-trip verifier)** — `ARVECTUM-1` was read natively on Windows; the offline ZIP and a fresh retrieval of the Mac mini primary copy each reported `30,996,168` bytes and SHA-256 `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`; both passed `tools/verify_windows_build_input_archive.ps1 -RequireCurrentRepositoryLocks` at repository commit `1429e55959e9a3940b1f2e03e84f18fa7b05de0c`; ZIP, sidecar and evidence files byte-matched across primary/offline copies.
- **DONE (P0.1 final offline storage human gate)** — after the Windows verifier, the operator safely ejected `ARVECTUM-1`, physically disconnected it and returned it to separate offline storage.
- **DONE — [Win] P0.1** — controlled Windows build-input archive closure is complete. Final non-secret evidence: `docs/evidence/P0_1_COMPLETION_EVIDENCE.json`. Canonical storage profile: `docs/P0_1_CONTROLLED_STORAGE_PROFILE.md`.
- **IN PROGRESS — [Win] P0.2** — preflight PASS and clean recovery baseline PASS. Fresh recovery source authority remains frozen at exact GitVerse commit `678efda6df68c93db8474c810abd73bca72735b2`; governed P0.1 archive identity remains `30,996,168` bytes / SHA-256 `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`. Oracle VirtualBox `7.2.14` revision `174565` is controlled and the dedicated `ARVECTUM-P0-2-RECOVERY` VM remains 4096 MB RAM, 2 vCPU, EFI, 64 GB dynamic disk and NIC `NONE`. Microsoft Windows 11 Enterprise Evaluation 25H2 x64 en-US ISO `Windows11_Ent_Eval_25H2_en-us_x64_v2.iso` was verified at `7,092,807,680` bytes and SHA-256 `A61ADEAB895EF5A4DB436E0A7011C92A2FF17BB0357F58B13BBC4062E535E7B9`, matching Microsoft-published hash evidence. A clean unattended x64 guest install completed with public networking never enabled; no product source, P0.1 archive or project build dependencies were introduced before shutdown and creation of verified snapshot `P0-2-CLEAN-BASELINE` UUID `e5abd145-780c-457c-8b8c-a4aa01581716`. Evidence: `docs/evidence/P0_2_CLEAN_BASELINE_EVIDENCE.json`. Portable recovery has **not** started. Next boundary: stage the exact frozen GitVerse source + governed P0.1 archive into the clean VM using local/offline transport while NIC remains `NONE`, verify both identities inside the guest, then run endpoint-denied portable recovery. Exact Inno Setup `6.7.1` remains separately blocked as `BLOCKED_MISSING_PRESTAGED_INNO_6_7_1`, so P0.2 remains open even if portable recovery later passes.
- **MEDIUM** — controlled mirrors for Linux/macOS build inputs and AppImage tooling where those artifacts are produced.

## 4. Per-application routing backlog

- **DONE** — APL-ROUTE-001 — platform-neutral routing rule model: application identity + all/domain/CIDR destination + direct/proxy action + deterministic schema.
- **DONE** — APL-ROUTE-002 — platform feasibility matrix.
  - Windows: WFP application-aware ALE connect-redirection is technically suitable.
  - Linux/Astra: controlled cgroup/socket identity + nftables/policy-routing is technically feasible but privileged and real-host dependent.
  - macOS: NetworkExtension per-app routing is entitlement/deployment/managed-configuration constrained; arbitrary consumer per-app routing is not promised.
- **AUTONOMOUS COMPLETE / LOCAL-NATIVE PENDING** — APL-ROUTE-003 control-plane prototype.
  - real read-only `FwpmGetAppIdFromFileName0` probe: done;
  - deterministic WFP filter-plan compiler: done;
  - Windows hosted probe: CI-governed;
  - live WFP callout/filter/proxy-service enforcement: not installed.
- **DONE** — APL-ROUTE-004 — durable routing ownership/recovery/security journal contract.

### APL-ROUTE-003 production STOP-GATE

Production WFP connect-redirection needs a kernel-mode callout/driver path. On normal supported Windows, new production kernel drivers are subject to Microsoft's Hardware Dev Center signing chain, and enrollment/signing requires Microsoft program participation plus an accepted EV code-signing identity. The Russian user-mode signing strategy does not substitute for this Windows kernel loading policy.

Therefore **do not implement or ship a production WFP kernel component yet**. First choose one product path:

1. accept the Microsoft Hardware Dev Center + accepted EV certificate dependency specifically for the optional per-app Windows SKU;
2. adopt a separately reviewed already-signed third-party enforcement component (which creates a new sovereignty/license/security dependency);
3. redesign the Windows per-app feature around a supported user-mode mechanism if one can satisfy the same semantics without a kernel callout;
4. defer Windows per-app routing while keeping system-proxy/domain/IP functionality production-ready.

Test-signing/developer modes are not accepted as a production-distribution workaround.

## 5. Final autonomous re-sweep result

The roadmap was re-evaluated after the autonomous sweep and its merge to `main`.

- **DONE** — CI/merge validation of the autonomous sweep.
- **DONE** — all repository-side Astra acceptance preparation currently possible without an Astra host.
- **DONE** — all repository-side macOS acceptance preparation currently possible without a real Mac.
- **DONE** — all APL-IP-001 engineering/provenance preparation currently possible without authorized human/legal judgment.
- **DONE** — all safe Windows WFP work short of the product/signing stop-gate and privileged native enforcement.
- **DONE** — CPython bootstrap identity pinning/verification, offline/hash-locked Windows build controls and P0.1 self-contained archive/offline-verifier preparation.
- **NO FURTHER AUTONOMOUS IMPLEMENTATION TASK IDENTIFIED** that can truthfully close one of the remaining gates without crossing a real-host, external-infrastructure, legal/human, signing, or product-policy boundary.

The remaining execution backlog is maintained in `docs/LOCAL_EXECUTION_BACKLOG.md`.

## 6. Immediate remaining execution order

1. **[Win] P0.2 stage controlled recovery inputs into clean VM:** start from verified snapshot `P0-2-CLEAN-BASELINE`, keep VirtualBox NIC `NONE`, transfer the exact frozen GitVerse source at `678efda6df68c93db8474c810abd73bca72735b2` plus the exact P0.1 controlled archive through host-local/offline transport, verify both identities inside the guest, and only then run the endpoint-denied portable recovery proof. Exact Inno Setup `6.7.1` must separately be brought under controlled/pre-staged storage before installer recovery can close P0.2.
2. **APL-LNX-010:** run real Astra acceptance; close Gate R8 only if evidence passes.
3. **APL-IP-001 human/legal sign-off:** significant-source review, artifact SBOM/notices reconciliation, chain-of-title evidence, then clean IP tag.
4. **ROUTE-003 product decision:** resolve the WFP kernel-signing stop-gate before native implementation.
5. After Windows routing policy is resolved/proven, consider Astra cgroup/nftables per-app prototype; macOS per-app only after entitlement/distribution proof.

## Completion rule

A task requiring a real target host, privileged native installation, hardware-backed signing identity, external platform enrollment, external controlled artifact storage, or legal/human judgment stays visibly pending until that evidence exists. CI simulations, mocks, hosted runners and documentation may reduce local work but never relabel that boundary as completed.
