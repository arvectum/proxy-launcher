# Arvectum Proxy Launcher — canonical roadmap

Updated: 2026-08-17
Canonical branch: `main`
Current product version: `0.2.3`

Status legend:

- **DONE** — implementation and required automated acceptance are complete.
- **AUTONOMOUS COMPLETE / LOCAL ACCEPTANCE PENDING** — all repository/CI work that can be completed without the target machine/hardware/native privileged installation is complete; remaining evidence requires local execution.
- **HUMAN/LEGAL PENDING** — engineering controls are complete, but a human/legal sign-off cannot be replaced by automation.
- **LOCAL/NATIVE DEBT** — the next meaningful step requires a real host, privileged/native component, hardware token, or equivalent local boundary.

## 0. Proven Windows/core baseline

The customer-proven Windows `0.2.3` system-proxy path remains the protected baseline. Autonomous roadmap work must not weaken or silently replace it.

- **DONE** — unified backend contract/regression matrix (APL-CORE-007).
- **DONE** — Windows portable/customer baseline and release/recovery safeguards already present in `main`.
- **DONE** — Windows runtime/installer/security/diagnostics/productization CI already present in `main`.
- **CONSTRAINT** — per-application routing is a new enforcement plane; it must not be smuggled into the proven Windows system-proxy path.

## 1. Linux / Astra Linux

- **DONE** — APL-LNX-006 — Linux diagnostics & support bundle.
- **DONE** — APL-LNX-007 — Debian `.deb` packaging. Merged independently as PR #66.
- **DONE** — APL-LNX-008 — AppImage packaging with hash-pinned build-only toolchain and extraction acceptance.
- **DONE** — APL-LNX-009 — Debian/Ubuntu 22.04/24.04 CI acceptance, including ephemeral dpkg install/remove and user-state preservation.
- **DONE** — APL-IP-002-LNX — Linux stack & dependency sovereignty audit (conditional pass).
- **AUTONOMOUS COMPLETE / LOCAL ACCEPTANCE PENDING** — APL-LNX-010 — real Astra Linux graphical/runtime/package acceptance.
- **LOCAL/NATIVE DEBT** — Gate R8 — may close only after APL-LNX-010 produces real Astra evidence.

### Linux release policy

For controlled Astra deployments, `.deb` is the preferred artifact because it avoids the additional AppImage runtime stub. AppImage remains an optional portable format.

## 2. macOS

- **DONE** — APL-MAC-001 — side-effect-free runtime and read-only `networksetup` preflight.
- **DONE** — APL-MAC-002 — capability/failure UX contract.
- **DONE** — APL-MAC-003 — privacy-bounded diagnostics/support bundle.
- **DONE** — APL-MAC-004 — deterministic `.app` packaging with stable bundle id and arm64/x64 CI.
- **DONE** — APL-MAC-005 — DMG packaging and read-only mount inspection.
- **DONE** — APL-MAC-006 — per-user LaunchAgent ownership/autostart model.
- **DONE** — APL-MAC-007 — packaging/recovery ownership contract tests.
- **DONE** — APL-IP-002-MAC — macOS stack & dependency sovereignty audit (conditional pass).
- **DONE** — post-roadmap integration hardening — macOS preflight is wired into the common backend operational gate before new `enable/sync` mutations; recovery/disable stays reachable.
- **AUTONOMOUS COMPLETE / LOCAL ACCEPTANCE PENDING** — APL-MAC-008 — real macOS GUI/system-proxy/autostart/crash-recovery acceptance.
- **LOCAL/NATIVE DEBT** — Gate R9 — may close only after APL-MAC-008 evidence is complete.

Apple production identity signing/notarization is not a functional correctness gate in the current Russian-first release strategy. It remains a later distribution-policy task unless priorities change.

## 3. Cross-platform sovereignty / IP

- **DONE** — APL-IP-002-WIN — Windows stack/dependency sovereignty audit already present; remediation findings remain binding.
- **DONE** — APL-IP-002-LNX.
- **DONE** — APL-IP-002-MAC.
- **DONE** — APL-IP-002-FINAL — consolidated cross-platform conditional verdict.
- **AUTONOMOUS COMPLETE / HUMAN/LEGAL PENDING** — APL-IP-001 — source provenance/human-authorship hardening.
  - source/build/config inventory + SHA-256 manifest: done;
  - third-party boundary/notices: done;
  - CI evidence: done;
  - human review of significant modules: pending;
  - chain-of-title/legal review for ООО «Арвектум»: pending;
  - clean IP baseline/tag: blocked until those reviews are signed off.

### Build-sovereignty remediation retained from APL-IP-002

- **HIGH PRIORITY** — Windows reproducible/offline build input closure: controlled CPython base, hash-bound wheelhouse and endpoint-denied/offline drill.
- **HIGH PRIORITY** — independent/self-hosted build recovery path so GitHub/public package registries are not single points of release failure.
- **MEDIUM PRIORITY** — controlled mirrors for Linux/macOS build inputs and AppImage tooling where those artifacts are produced.

## 4. Per-application routing backlog

- **DONE** — APL-ROUTE-001 — platform-neutral routing rule model: application identity + all/domain/CIDR destination + direct/proxy action + deterministic schema.
- **DONE** — APL-ROUTE-002 — feasibility matrix based on platform-native mechanisms.
  - Windows: first target through WFP application-aware ALE connect-redirection architecture.
  - Linux/Astra: technically feasible through controlled cgroup/socket identity + nftables/policy-routing architecture; requires real-host privileged acceptance.
  - macOS: NetworkExtension per-app path is entitlement/deployment/managed-configuration constrained; arbitrary consumer per-app routing is not promised.
- **AUTONOMOUS COMPLETE / LOCAL/NATIVE DEBT** — APL-ROUTE-003 — Windows application-routing prototype.
  - real read-only WFP application-id retrieval: done;
  - deterministic filter-plan compiler: done;
  - Windows hosted WFP probe: done/CI-governed;
  - live WFP callout/filter/proxy-service enforcement: pending native privileged implementation and real Windows acceptance.
- **DONE** — APL-ROUTE-004 — durable routing ownership/recovery/security journal contract.

### Next routing implementation sequence

1. native Windows WFP enforcement component + local proxy loop-prevention design;
2. install/update/remove ownership and production signing for the native component;
3. real Windows per-app direct/proxy acceptance including crash/reboot/rollback;
4. only after Windows proof, Astra cgroup/nftables prototype and capability acceptance;
5. macOS per-app routing only after entitlement/distribution-model proof.

## 5. Immediate next execution order

The next tasks are ordered by risk reduction, not by platform aesthetics:

1. **Windows build-sovereignty closure** — remove public-network/build-channel single points of failure as far as automation allows; retain a final independent/local offline drill.
2. **Prepare one-command real Astra acceptance evidence collection**, then execute it on the target Astra host when available.
3. **Prepare one-command real macOS acceptance evidence collection**, then execute it on a real Mac when available.
4. **Native WFP implementation specification/scaffold** without installing it into the proven customer baseline; live enforcement remains a separate local acceptance step.
5. **Human/legal APL-IP-001 sign-off package** after final release artifacts/SBOM are known.
6. **Gate R8/R9 closure** only from real-host evidence; never from hosted CI alone.

## Completion rule

A task that requires a real target host, privileged native installation, hardware-backed signing identity, or legal/human judgment must remain visibly pending until that evidence exists. CI simulation, mocks, hosted runners and documentation may reduce the local work but may not be used to relabel that boundary as completed.
