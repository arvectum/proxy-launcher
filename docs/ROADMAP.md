# Arvectum Proxy Launcher — canonical roadmap

Updated: 2026-08-17
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
- **DONE** — Gate R9 — close only from APL-MAC-008 real-host evidence.

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
- **AUTONOMOUS COMPLETE / LOCAL ACCEPTANCE PENDING — [Win] P0.1** — copy the verified self-contained archive into an Arvectum/Russian-controlled artifact perimeter, verify the stored/retrieved bytes offline and record non-secret storage/retention/offline-copy evidence. Canonical runbook: `docs/P0_1_WINDOWS_CONTROLLED_CPYTHON_WHEELHOUSE_ARCHIVE.md`.
- **LOCAL/INFRA DEBT — HIGH — [Win] P0.2** — perform the independent/self-hosted/GitVerse recovery build with public package endpoints denied and compare exact release evidence using only the P0.1 controlled archive.
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

1. **[Win] P0.1 local/infrastructure acceptance:** acquire the governed bytes, create/verify the self-contained archive, store it in the selected Arvectum/Russian-controlled perimeter, verify the controlled copy and record storage/offline-copy evidence.
2. **[Win] P0.2 sovereign recovery build:** run an independent endpoint-denied/self-hosted/GitVerse recovery build using only the P0.1 controlled archive and compare release evidence.
3. **APL-LNX-010:** run real Astra acceptance; close Gate R8 only if evidence passes.
4. **APL-IP-001 human/legal sign-off:** significant-source review, artifact SBOM/notices reconciliation, chain-of-title evidence, then clean IP tag.
5. **ROUTE-003 product decision:** resolve the WFP kernel-signing stop-gate before native implementation.
6. **APL-MAC-008:** run real Mac acceptance; close Gate R9 only from real-host evidence.
7. After Windows routing policy is resolved/proven, consider Astra cgroup/nftables per-app prototype; macOS per-app only after entitlement/distribution proof.

## Completion rule

A task requiring a real target host, privileged native installation, hardware-backed signing identity, external platform enrollment, external controlled artifact storage, or legal/human judgment stays visibly pending until that evidence exists. CI simulations, mocks, hosted runners and documentation may reduce local work but never relabel that boundary as completed.
