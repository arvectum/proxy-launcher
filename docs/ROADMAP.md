# Arvectum Proxy Launcher — canonical roadmap

Updated: 2026-08-21
Canonical branch: `main`
Current product version: `0.2.3`

Status legend:

- **DONE** — implementation and required acceptance are complete.
- **ACTIVE** — current execution priority.
- **PLANNED / NEXT** — deliberately queued immediately after the active prerequisite.
- **PAUSED / EXTERNAL ENVIRONMENT** — work is deliberately paused until a suitable external/physical environment exists; do not keep retrying unavailable infrastructure.
- **AUTONOMOUS COMPLETE / LOCAL ACCEPTANCE PENDING** — repository/CI work is complete; remaining evidence requires the target machine or privileged local execution.
- **BLOCKED / EXTERNAL HOST REQUIRED** — repository/CI work is complete enough to stop local execution; the remaining gate requires a separate eligible physical host and must not be forced on the normal owner workstation.
- **HUMAN/LEGAL PENDING** — engineering controls are complete, but judgment/sign-off cannot be replaced by automation.
- **DEFERRED / NOT RELEASE BLOCKER** — valuable hardening/resilience work intentionally removed from the current release critical path.
- **STOP-GATE** — do not continue implementation until the named product/legal/infrastructure decision is made.

## 0. Proven Windows/core baseline

The customer-proven Windows `0.2.3` system-proxy path remains the protected production baseline. New routing, refactor, or release work must not silently replace or destabilize it.

- **DONE** — APL-CORE-007 — unified backend contract & regression matrix.
- **DONE** — Windows portable/customer-confirmed `0.2.3` baseline and release/recovery safeguards are present in `main`.
- **DONE** — Windows runtime/security/diagnostics/productization CI is present in `main`.
- **DONE** — P0.1 controlled Windows build-input archive closure. Canonical evidence: `docs/evidence/P0_1_COMPLETION_EVIDENCE.json`.
- **DONE** — exact governed CPython `3.12.10` x64 bootstrap and exact eight-wheel hash-locked Windows build set are archived and independently retained.
- **CONSTRAINT** — the sealed `0.2.3` source/release evidence is an immutable comparison baseline for APL-IP-003; the refactor must not rewrite or relabel that historical release.
- **CONSTRAINT** — per-application routing is a new enforcement plane and remains separated from the proven system-proxy baseline.

### P0.2 independent clean-machine offline rebuild drill

- **DEFERRED / NOT RELEASE BLOCKER** — the full endpoint-denied clean-machine reproduction drill remains resilience/supply-chain hardening, not a prerequisite for shipping the current Windows product.
- The abandoned VM path remains historical/forensic evidence only and must not be revived to satisfy this drill or any other gate.

## 1. Windows production release contour

### Inno Setup 6.7.1 / production installer

- **DONE** — exact Inno Setup `6.7.1` controlled acquisition and production installer closure.
- **DONE** — exact upstream installer size/SHA-256, Authenticode publisher, portable ISCC version/hash, canonical portable build and canonical `0.2.3` installer build are verified and evidenced.
- **DONE** — portable EXE SHA-256 `f8d98f987ce92dee7979b12b69a56d120ddb12244bebe2559bc51359a53f9c7a`.
- **DONE** — portable ZIP SHA-256 `62d313547b4d8c2c8e6951d6cd866bb954fdf199ad7650063c8ed3bfbc455801`.
- **DONE** — installer SHA-256 `5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414`.
- Canonical evidence: `docs/evidence/WINDOWS_INNO_6_7_1_PRODUCTION_BUILD_EVIDENCE.json`.

### Windows production signing / release package

- **DONE** — `[Win] Russian-first production signing` repository implementation and physical owner-station acceptance.
- **DONE** — one canonical fail-closed owner-operated entry point: `tools/windows_russian_production_signing.ps1`.
- **DONE** — physical ceremony completed on 2026-08-20 with tag `v0.2.3-ru.2` at release-policy commit `47823585c42da54ab51dc2246583dc24d74d4ba6`.
- **DONE** — detached CryptoPro/Rutoken manifest verification, exact signed release-set verification, tamper-negative test and publication gate all passed.
- **TRUST BOUNDARY** — the governed Russian certificate proves release provenance/integrity; embedded Authenticode/SmartScreen/Smart App Control execution trust is not claimed.
- Canonical evidence: `docs/evidence/WINDOWS_RUSSIAN_PRODUCTION_SIGNING_ACCEPTANCE_2026-08-20.json`.

### APL-WIN-014 — Windows application-control execution compatibility

- **BLOCKED / EXTERNAL HOST REQUIRED** — autonomous tooling and owner-host diagnostics are complete; final App Control for Business PASS requires a separate eligible physical Windows 11 Pro/Enterprise/Education host.
- **SAFETY BLOCK** — the normal Windows 11 Home owner workstation is diagnostics-only. Do not deploy/remove `.cip` policies, alter Smart App Control, replace the live Arvectum build, stop AmneziaVPN/NGate/proxy components, or run destructive acceptance there.
- Canonical runbook: `docs/APL_WIN_014_LOCAL_GATE.md`.

### APL-REL-014 — exact signed-set lifecycle acceptance

- **BLOCKED / EXTERNAL HOST REQUIRED** — repository/CI lifecycle automation is complete, but destructive physical acceptance is prohibited on the normal owner workstation.
- **RECOVERY DONE** — the owner workstation was recovered after the 2026-08-20 incident without weakening Windows security controls; the live proxy stack must remain protected.
- **FINAL LOCAL GATE** — use only the same class of separate physical Windows acceptance host required for APL-WIN-014. Do not return to the abandoned VM path.
- Incident evidence: `docs/evidence/APL_REL_014_OWNER_HOST_INCIDENT_2026-08-20.md`.

International Microsoft/GlobalSign-oriented distribution remains lower priority and must not silently replace the Russian-first strategy.

## 2. Linux / Astra Linux

- **DONE** — APL-LNX-006 — Linux diagnostics & support bundle.
- **DONE** — APL-LNX-007 — Debian `.deb` packaging.
- **DONE** — APL-LNX-008 — AppImage packaging with hash-pinned build-only toolchain.
- **DONE** — APL-LNX-009 — Ubuntu 22.04/24.04 CI acceptance.
- **DONE** — APL-IP-002-LNX — Linux stack/dependency sovereignty audit (conditional pass).
- **PAUSED / EXTERNAL ENVIRONMENT** — APL-LNX-010 — real Astra Linux graphical/runtime/package acceptance. Resume only when a suitable real Astra host exists; CI/another distro is not a substitute.

For controlled Astra deployments, `.deb` remains the preferred package. AppImage remains optional and is **not yet cleared for promoted commercial distribution** until the exact type-2 runtime/transitive-license obligations recorded by APL-IP-001 are reviewed/satisfied.

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

### APL-IP-001 — source provenance / human-authorship baseline

- **HUMAN/LEGAL PENDING — AUTONOMOUS CARRY-FORWARD CLOSURE COMPLETE**.
- exact preserved historical review candidate: `7c3bdbd005e6ff27db8f5a00071dc81c8595dd9b`;
- candidate tree: `9c372b440919b3b9e69d78ab0a85dca3f387d5af`;
- source/build/config inventory + SHA-256 manifest: done;
- provenance scanner hardening: done;
- automated provenance findings on the candidate: `0`;
- significant-source pre-review: 34 files; build/release pre-review: 75 files;
- public OSS similarity sample: no external matches found;
- unknown dependencies: `0`;
- exact sealed `0.2.3` product-source drift from artifact build to review candidate: `0` significant source files;
- human factual confirmation: done and recorded in `docs/evidence/APL_IP_001_HUMAN_FACT_CONFIRMATION_2026-08-21.md`;
- all `arvectum` / `arutyunoveth` human Git identities are confirmed as one human developer/project owner;
- `OpenAI <noreply@openai.com>` is retained as AI/tool identity and GitHub Actions as automation; neither is relabeled as a human author;
- base Arvectum logo is confirmed self-authored by the project owner;
- conscious copying from Stack Overflow/GitHub/foreign projects was denied by the human author; AI-generated code was human-reviewed and accepted/corrected as part of development;
- author-to-ООО rights instrument template: done (`docs/legal/APL_IP_001_RIGHTS_ASSIGNMENT_TEMPLATE.md`);
- **remaining human/legal prerequisite before APL-IP-003:** execute/retain the author-to-ООО rights basis (or independently verified equivalent basis) and record a stable non-secret evidence reference;
- build SBOM boundary is explicitly classified as build-dependency SBOM, not universal final-artifact SBOM;
- Windows release-set notice/license delivery: reconciled against existing exact production evidence;
- Linux `.deb`: notice/license packaging contract reconciled;
- Linux AppImage: notice delivery remediated/test-protected, but promoted commercial distribution remains on a bounded hold because the exact runtime license identifies separately licensed statically linked components;
- macOS `.app`/DMG: notice delivery remediated/test-protected; exact new artifact proof belongs to the post-refactor candidate/build;
- platform/license carry-forward evidence: `docs/evidence/APL_IP_001_PLATFORM_LICENSE_RECONCILIATION_2026-08-21.md`;
- carry-forward closure evidence: `docs/evidence/APL_IP_001_CARRY_FORWARD_CLOSURE_2026-08-21.md`;
- current sign-off record: `docs/APL_IP_001_HUMAN_LEGAL_SIGNOFF.md`.

**Sequencing decision:** the repository/engineering carry-forward is closed. Preserve the exact pre-refactor evidence baseline and do not create a clean-IP tag on it. After the human/legal rights-basis execution reference exists, execute APL-IP-003, then perform one new exact post-refactor source/provenance/SBOM/platform-license/human/legal review and create the clean-IP tag only after explicit APPROVED status.

### APL-IP-003 — Arvectum canonical source refactor

- **PLANNED / NEXT — WAITING ONLY FOR THE NAMED APL-IP-001 HUMAN/LEGAL RIGHTS-BASIS EXECUTION REFERENCE**.
- Canonical task specification: `docs/APL_IP_003_CANONICAL_SOURCE_REFACTOR.md`.
- Goal: produce one coherent Arvectum source edition with unified architecture, terminology, code style, repository identity and ownership conventions while preserving truthful Git/provenance history.
- Add a governed `.mailmap` to normalize the owner's historical `arvectum` / `arutyunoveth` identities without rewriting commits.
- Normalize maintained repository references to `arvectum/proxy-launcher`; preserve required upstream dependency/license/provenance links.
- Do not remap `OpenAI` or bot identities to the human author and do not rewrite Git history.
- Normalize naming, typing, docstrings, logging, error boundaries, configuration/state handling and platform backend structure.
- Reduce obsolete legacy/compatibility layers and duplicated scaffolding where tests prove removal is safe.
- Explicit target principles: ownership, fail-closed mutation, deterministic recovery, capability-first platform abstraction, control-plane/enforcement-plane separation, immutable/verifiable evidence.
- Refactor incrementally under full regression and packaging/build-contract checks; do not combine unrelated product features with structural cleanup.
- Carry forward the APL-IP-001 package-notice hardening; do not regress the `.deb`, AppImage or macOS notice contracts.
- The sealed Windows `0.2.3` release remains immutable and serves as the behavioural/release reference baseline.
- After refactor: select a new exact candidate, regenerate provenance/SBOM evidence, repeat similarity/provenance review, build/reconcile the promoted platform artifacts, perform bounded human/legal review, and create the clean-IP tag only after APPROVED.

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

1. **HUMAN/LEGAL PENDING — APL-IP-001 rights-basis execution:** repository carry-forward closure is complete. Execute/retain the author→ООО «Арвектум» rights instrument (or establish an independently verified equivalent rights basis) and record a stable non-secret evidence reference. Do not create a pre-refactor clean-IP tag.
2. **NEXT — APL-IP-003:** immediately after the rights-basis reference exists, perform the full Arvectum canonical source refactor under protected `0.2.3` behavioural/release baselines and retain all APL-IP-001 package-notice hardening.
3. **POST-REFACTOR IP REVIEW:** select the new exact canonical candidate, regenerate provenance/SBOM evidence, repeat bounded source/license/human review, build/reconcile promoted platform artifacts, then create the clean-IP baseline/tag only after explicit APPROVED.
4. **APL-ROUTE-003:** only after the canonical source/IP baseline, make the product decision on the Windows per-app enforcement/signing path.
5. **PAUSED — APL-LNX-010:** resume real Astra Linux acceptance only when a suitable real Astra host is available.
6. **BLOCKED — APL-WIN-014:** final App Control for Business acceptance only on a separate eligible physical Windows host; never on the normal owner workstation and never via the abandoned VM path.
7. **BLOCKED — APL-REL-014:** exact signed-set destructive lifecycle acceptance only on the separate physical Windows acceptance host.
8. **Deferred hardening:** independent clean-machine endpoint-denied Windows rebuild drill; controlled Linux/macOS build-input mirrors; later international signing/notarization paths.

## Completion rule

Real-host, signing, external-platform, infrastructure and legal/human gates stay visibly pending until their named evidence exists. CI simulations, mocks and documentation may reduce local work but do not replace those boundaries. Historical provenance must remain truthful: canonicalization may normalize current code, repository references and human identity presentation through `.mailmap`, but must not rewrite commits or relabel AI/bot identities as human authors. The normal owner Windows workstation remains diagnostics-only for APL-WIN-014/APL-REL-014. The abandoned VM path remains out of scope.
