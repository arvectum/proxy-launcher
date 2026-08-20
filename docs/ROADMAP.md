# Arvectum Proxy Launcher — canonical roadmap

Updated: 2026-08-20
Canonical branch: `main`
Current product version: `0.2.3`

Status legend:

- **DONE** — implementation and required acceptance are complete.
- **ACTIVE** — current execution priority.
- **AUTONOMOUS COMPLETE / LOCAL ACCEPTANCE PENDING** — repository/CI work is complete; remaining evidence requires the target machine or privileged local execution.
- **HUMAN/LEGAL PENDING** — engineering controls are complete, but judgment/sign-off cannot be replaced by automation.
- **DEFERRED / NOT RELEASE BLOCKER** — valuable hardening/resilience work intentionally removed from the current release critical path.
- **STOP-GATE** — do not continue implementation until the named product/legal/infrastructure decision is made.

## 0. Proven Windows/core baseline

The customer-proven Windows `0.2.3` system-proxy path remains the protected production baseline. New routing or release work must not silently replace or destabilize it.

- **DONE** — APL-CORE-007 — unified backend contract & regression matrix.
- **DONE** — Windows portable/customer-confirmed `0.2.3` baseline and release/recovery safeguards are present in `main`.
- **DONE** — Windows runtime/security/diagnostics/productization CI is present in `main`.
- **DONE** — P0.1 controlled Windows build-input archive closure. Canonical evidence: `docs/evidence/P0_1_COMPLETION_EVIDENCE.json`.
- **DONE** — exact governed CPython `3.12.10` x64 bootstrap and exact eight-wheel hash-locked Windows build set are archived and independently retained.
- **CONSTRAINT** — per-application routing is a new enforcement plane and remains separated from the proven system-proxy baseline.

### P0.2 independent clean-machine offline rebuild drill

- **DEFERRED / NOT RELEASE BLOCKER** — the full endpoint-denied clean-machine reproduction drill is retained as resilience/supply-chain hardening, but it no longer blocks the Windows production release.
- The product already has a customer-proven sealed Windows `0.2.3` artifact and P0.1 preserves the governed CPython/wheelhouse inputs required for a future independent rebuild.
- The attempted VirtualBox recovery path exposed host-specific virtualization/VBS/NEM incompatibilities and was stopped rather than weakening Windows security controls or bypassing Windows 11 requirements.
- Existing P0.2 evidence and failed recovery-environment artifacts remain historical/forensic evidence; they must not be relabeled as a successful independent rebuild.
- Future execution is hypervisor-independent: when a suitable clean Windows machine/environment is available, perform one bounded offline rebuild using the governed P0.1 archive, frozen source authority, endpoint denial, full tests/package contract/SBOM, and artifact comparison.
- Future completion of this drill is useful for disaster recovery and supply-chain assurance, not a prerequisite for shipping the current Windows product.

## 1. Windows production release contour

### Inno Setup 6.7.1 / production installer

- **DONE** — exact Inno Setup `6.7.1` controlled acquisition and production installer closure.
- **DONE** — exact upstream Inno Setup `6.7.1` controlled acquisition; exact installer size/SHA-256 verified against the repository lock (`10619024` bytes, `4d11e8050b6185e0d49bd9e8cc661a7a59f44959a621d31d11033124c4e8a7b0`).
- **DONE** — Authenticode `Valid` / publisher `Pyrsys B.V.`; controlled copy retained under Arvectum control.
- **DONE** — exact portable ISCC `6.7.1` installed and verified via compiler-preprocessor-ver `0x06070100`; ISCC SHA-256 `eb6f4410c8db367a5f74127e8025ad2ccacc0afabbe783959d237df3050f97fb`.
- **DONE** — canonical Windows portable build PASS; `dependency_mode=offline-hash-locked`; 521 tests PASS; portable EXE SHA-256 `f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a`; portable ZIP SHA-256 `62d313547b4d8c2c8e6951d6cd866bb954fdf199ad7650063c8ed3bfbc455801`.
- **DONE** — canonical `0.2.3` installer build PASS; installer SHA-256 `5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414`.
- The sealed installer input is intentionally Authenticode-unsigned. The Russian-first contour signs the exact final release manifest with the governed CryptoPro/Rutoken identity and does not mutate or misrepresent the installer as Microsoft-native signed code.
- Canonical evidence: `docs/evidence/WINDOWS_INNO_6_7_1_PRODUCTION_BUILD_EVIDENCE.json`.

### Windows production signing / release package

- **DONE** — `[Win] Russian-first production signing` repository implementation and physical owner-station acceptance.
- **DONE** — one canonical fail-closed owner-operated entry point: `tools/windows_russian_production_signing.ps1`.
- **DONE** — exact `0.2.3` portable ZIP and installer are bound to the production-build evidence by filename, SHA-256 and installer size before any signing step.
- **DONE** — dual-commit provenance preserves the real artifact build commit separately from the later release-policy commit; runtime/build-input drift after the sealed build forces a rebuild instead of silently reusing stale binaries.
- **DONE** — canonical staging includes portable + installer + build provenance + notices/license + end-user verification UX before manifest generation/signing.
- **DONE** — APL-REL-011 detached CryptoPro/Rutoken manifest signing/verification and APL-REL-013 fail-closed publication gate are composed into the same ceremony.
- **DONE** — Windows PowerShell 5.1 compatibility is covered across the orchestrator, UTF-8 child-script boundary, CryptoPro native stderr handling, signer and end-user verifier.
- **DONE** — physical ceremony completed on 2026-08-20 with tag `v0.2.3-ru.2` at release-policy commit `47823585c42da54ab51dc2246583dc24d74d4ba6`.
- **DONE** — APL-REL-011 detached signature verification PASS; APL-REL-012 exact signed release-set verification PASS; mandatory tampered-copy test PASS_EXPECTED_FAILURE; APL-REL-013 publication decision `PUBLISH`.
- **DONE** — canonical signed release directory and external `.production-release-gate.json` publication decision were retained on the owner-operated Windows host.
- **TRUST BOUNDARY** — the currently governed certificate remains `RELEASE-EVIDENCE-ONLY`; embedded Authenticode/SmartScreen/Smart App Control execution trust is not claimed.
- **DISCOVERED DISTRIBUTION BOUNDARY** — a real Windows owner workstation with application-control enforcement blocked the unsigned legacy Arvectum EXE during APL-REL-014 restoration. Detached CryptoPro/Rutoken evidence therefore remains necessary for Russian release provenance but is insufficient by itself for Windows execution trust on application-control-enforced hosts.
- Canonical repository evidence: `docs/evidence/WINDOWS_RUSSIAN_PRODUCTION_SIGNING_ACCEPTANCE_2026-08-20.json`.
- Runbook: `docs/WINDOWS_RUSSIAN_FIRST_PRODUCTION_SIGNING.md`.

### APL-WIN-014 — Windows application-control execution compatibility

- **AUTONOMOUS COMPLETE / REAL APP-CONTROL ACCEPTANCE PENDING** — implementation merged by PR #108 at `bcadbf3143dcee175b589827ba8617c380e312f1`.
- **DONE** — Russian release provenance and Windows execution trust are explicitly separated; detached CryptoPro/Rutoken evidence is never represented as Authenticode/Smart App Control trust.
- **DONE** — read-only assessment: `tools/windows_app_control_assess.ps1`.
- **DONE** — enterprise supplemental exact-hash trust-pack generator: `tools/windows_app_control_enterprise_trust_pack.ps1` with `BootstrapHash` and lifecycle-capable `ReferenceFullHash` modes.
- **DONE** — customer Managed Installer deployment profile is documented as the preferred scalable enterprise path when supported; Arvectum tooling does not designate or deploy the customer's managed installer.
- **DONE** — owner/developer safe source-mode profile: `tools/windows_owner_source_mode.ps1`; no Smart App Control/App Control mutation and no dependency on the blocked legacy EXE.
- **DONE** — PowerShell 5.1 parser, repository safety contracts and Windows ConfigCI supplemental-policy conversion smoke PASS; portable, installer lifecycle E2E/Gate R6, SAST, SBOM, provenance, secret and dependency gates PASS on the merged head.
- **LOCAL GATE** — prove execution on a representative organization-managed Windows 11 host/VM with App Control for Business enabled: exact release verification, supplemental/base-policy compatibility, Setup, first launch, core/GUI/PAC, rollback, repair, upgrade and uninstall without disabling host protection.
- **PUBLIC UNMANAGED BOUNDARY** — deterministic Smart App Control admission for public unmanaged Windows remains unresolved until a supported trusted embedded code-signing path exists; international public code-signing remains a lower-priority fallback.
- Canonical task definition: `docs/WINDOWS_APP_CONTROL_COMPATIBILITY.md`.

### APL-REL-014 — exact signed-set lifecycle acceptance

- **AUTONOMOUS COMPLETE / ISOLATED WINDOWS ACCEPTANCE PENDING** — repository/CI lifecycle automation is complete; real destructive acceptance must run only in a disposable/isolated Windows VM or dedicated acceptance host.
- **DONE** — canonical script: `tools/windows_signed_set_lifecycle_acceptance.ps1`.
- **DONE** — release identity is pinned to version `0.2.3`, tag `v0.2.3-ru.2`, release-policy commit `47823585c42da54ab51dc2246583dc24d74d4ba6`, governed signer thumbprint, and sealed portable/installer hashes.
- **DONE** — exact Russian release verification runs before and after lifecycle execution; the signed release directory is never mutated by the acceptance script.
- **DONE** — lifecycle phases are automated: fresh install → `--status` smoke → same-version repair → deliberate binary/stale-state corruption → cached repair recovery → uninstall.
- **DONE** — cached repair installer must hash-identically match the signed production installer.
- **DONE** — user configuration preservation and foreign-autostart ownership boundaries are tested.
- **INCIDENT / OWNER-HOST PROHIBITION** — migration-style execution on the normal owner workstation on 2026-08-20 restored install/state trees but Windows application-control enforcement blocked restart of the legacy EXE. The run remained `BLOCK`; canonical lifecycle phases did not complete.
- **RECOVERY DONE** — owner workstation was recovered from source without disabling Windows protection; proxy settings, PAC, core and GUI returned to a healthy state. Rescue evidence is retained.
- **LOCAL GATE** — execute APL-REL-014 only in a disposable/isolated Windows acceptance environment and retain `result=PASS` + `environment_restored=true`. Do not run destructive acceptance on the normal owner workstation again.
- Incident evidence: `docs/evidence/APL_REL_014_OWNER_HOST_INCIDENT_2026-08-20.md`.
- Runbook: `docs/WINDOWS_SIGNED_SET_LIFECYCLE_ACCEPTANCE.md`.

International Microsoft/GlobalSign-oriented distribution remains lower priority; it may be evaluated only as a fallback under APL-WIN-014 rather than silently replacing the Russian-first strategy.

## 2. Linux / Astra Linux

- **DONE** — APL-LNX-006 — Linux diagnostics & support bundle.
- **DONE** — APL-LNX-007 — Debian `.deb` packaging.
- **DONE** — APL-LNX-008 — AppImage packaging with hash-pinned build-only toolchain.
- **DONE** — APL-LNX-009 — Ubuntu 22.04/24.04 CI acceptance.
- **DONE** — APL-IP-002-LNX — Linux stack/dependency sovereignty audit (conditional pass).
- **AUTONOMOUS COMPLETE / LOCAL ACCEPTANCE PENDING** — APL-LNX-010 — real Astra Linux graphical/runtime/package acceptance.
- **LOCAL GATE** — Gate R8 closes only from real Astra host evidence.

For controlled Astra deployments, `.deb` remains the preferred package; AppImage is optional.

## 3. macOS

- **DONE** — APL-MAC-001..007 runtime/preflight/diagnostics/packaging/autostart/recovery work.
- **DONE** — APL-IP-002-MAC — macOS stack/dependency sovereignty audit (conditional pass).
- **DONE** — APL-MAC-008 — real macOS GUI/system-proxy/autostart/crash-recovery acceptance.
- **DONE** — Gate R9.

Apple production identity signing/notarization remains a later distribution-policy task under the Russian-first strategy.

## 4. Cross-platform sovereignty / IP

- **DONE** — APL-IP-002-WIN.
- **DONE** — APL-IP-002-LNX.
- **DONE** — APL-IP-002-MAC.
- **DONE** — APL-IP-002-FINAL consolidated conditional verdict.
- **AUTONOMOUS COMPLETE / HUMAN/LEGAL PENDING** — APL-IP-001 — source provenance/human-authorship hardening.
  - source/build/config inventory + SHA-256 manifest: done;
  - third-party boundary/notices: done;
  - CI evidence: done;
  - sign-off record/template: done (`docs/APL_IP_001_HUMAN_LEGAL_SIGNOFF.md`);
  - authorized human review of significant modules: pending;
  - chain-of-title/legal review for ООО «Арвектум»: pending;
  - clean IP baseline/tag: only after those reviews are approved.

Controlled Linux/macOS build-input mirrors remain medium-priority sovereignty hardening after the primary Windows release contour.

## 5. Per-application routing backlog

- **DONE** — APL-ROUTE-001 — platform-neutral routing rule model.
- **DONE** — APL-ROUTE-002 — platform feasibility matrix.
- **AUTONOMOUS COMPLETE / LOCAL-NATIVE PENDING** — APL-ROUTE-003 control-plane prototype.
- **DONE** — APL-ROUTE-004 — durable routing ownership/recovery/security journal contract.

### APL-ROUTE-003 production STOP-GATE

Production Windows WFP connect-redirection requires a kernel/native enforcement path and an external Windows kernel-signing/distribution decision. Do not implement or ship a production WFP kernel component until one path is chosen deliberately:

1. accept Microsoft Hardware Dev Center + accepted EV identity dependency for an optional per-app Windows SKU;
2. adopt a separately reviewed already-signed third-party enforcement component;
3. prove a supported user-mode architecture with equivalent semantics;
4. defer Windows per-app routing while keeping system-proxy/domain/IP functionality production-ready.

Test-signing/developer modes are not accepted as a production workaround.

## 6. Immediate execution order

1. **APL-WIN-014 local gate:** real App Control for Business acceptance on a representative organization-managed Windows 11 VM/host; owner workstation is not the destructive test environment.
2. **APL-REL-014:** run exact signed-set lifecycle acceptance in an isolated/disposable Windows acceptance environment only; never again on the normal owner workstation.
3. **APL-LNX-010:** real Astra Linux acceptance; close Gate R8 only from real-host evidence.
4. **APL-IP-001:** authorized human/legal sign-off and clean IP baseline/tag.
5. **APL-ROUTE-003:** product decision on the Windows per-app enforcement/signing path.
6. **Deferred hardening:** independent clean-machine endpoint-denied Windows rebuild drill when a suitable environment is available; controlled Linux/macOS build-input mirrors; later international signing/notarization paths.

## Completion rule

Real-host, signing, external-platform, infrastructure and legal/human gates stay visibly pending until their named evidence exists. CI simulations, mocks and documentation may reduce local work but do not replace those boundaries. Destructive Windows lifecycle acceptance is now additionally constrained to disposable/isolated acceptance environments. Deferred resilience work must not be allowed to re-enter the release critical path without an explicit product-risk decision.
