# APL-IP-003 — Arvectum canonical source refactor

Status: **ACTIVE — SLICES 1–10 MERGED; FINAL CLEAN-IP APPROVAL STILL HUMAN/LEGAL GATED**

## Goal

Create a unified, intentionally Arvectum-authored canonical source edition of Proxy Launcher without rewriting or falsifying historical provenance.

The task is an engineering refactor, not an attempt to erase AI assistance, third-party dependency history, or Git evidence. Historical commits remain intact. The resulting source tree should use one coherent architecture, terminology, code style, repository identity, and ownership model.

## Preconditions and standing gates

- Preserve the sealed Windows `0.2.3` release and its evidence as an immutable behavioural/release baseline.
- The APL-IP-001 autonomous provenance/carry-forward baseline is complete enough to preserve the pre-refactor record. Its named author-to-ООО rights-basis execution reference remains **HUMAN/LEGAL PENDING** and is still required before any post-refactor clean-IP candidate can be declared APPROVED or tagged.
- Do not create or rewrite historical commits to manufacture authorship.
- Do not weaken tests, security controls, recovery semantics, platform ownership boundaries, or release gates.
- Do not disturb the live owner Windows proxy/VPN/network stack during refactor work.

## Current bounded execution

- **DONE — Slice 1:** system-proxy runtime composition extraction. Canonical merge baseline: `94e60fb51fe7d0b8f9d650025fce35bf69638bb6`.
- **DONE — Slice 2:** application filesystem & portable lifecycle extraction. PR `#120`, merge commit `f2507cda77ded8e21e5e3a855853d94d79ef343f`.
- **DONE — Slice 3:** configuration loading/validation, atomic persistence and configuration-recovery ownership extraction. PR `#122`, merge commit `9a59d1dfe5687fb8fafa59811be8c2fff994c9b0`. Canonical owner: `configuration_storage.py`. All 18 PR workflows completed successfully; closure evidence is recorded in `docs/evidence/APL_IP_003_SLICE_3_CONFIGURATION_STORAGE.md`.
- **DONE — Slice 4:** platform-neutral routing-policy ownership extraction. PR `#124`, merge commit `0a4256d0f16bb0c798f96f9d4a618564f38b92c5`. Canonical owner: `routing_policy.py`. All 18 PR workflows completed successfully; closure evidence is recorded in `docs/evidence/APL_IP_003_SLICE_4_ROUTING_POLICY.md`.
- **DONE — Slice 5:** local HTTP/SOCKS/PAC transport-server ownership extraction. PR `#126`, merge commit `e2733e19172bff0c1c15df070fb6e1951bc50c2c`. Canonical owner: `local_proxy_transport.py`. All 18 PR workflows completed successfully; closure evidence is recorded in `docs/evidence/APL_IP_003_SLICE_5_LOCAL_PROXY_TRANSPORT.md`.
- **DONE — Slice 6:** process supervision / runtime-status ownership extraction. PR `#128`, merge commit `82333217bb992c00c22663d5b636f90252c05171`. Canonical owner: `process_supervision.py`. All 18 PR workflows completed successfully; the canonical-source guard was extended through Slice 6; closure evidence is recorded in `docs/evidence/APL_IP_003_SLICE_6_PROCESS_SUPERVISION.md`.
- **DONE — Slice 7:** CLI / application runtime orchestration ownership extraction. PR `#130`, merge commit `c176f51e2c85185e2319a5f8669a14c9db18e50d`. Canonical owner: `application_runtime.py`. All 18 PR workflows completed successfully; exact `0.2.3` CLI/runtime ordering, messages and exit-code behaviour remain the contract; closure evidence is recorded in `docs/evidence/APL_IP_003_SLICE_7_APPLICATION_RUNTIME.md`.
- **DONE — Slice 8:** Windows WinINET / proxy-environment persistence and system-proxy implementation ownership extraction. PR `#132`, merge commit `cd1f032c1505e3123779b1ac0f283513fce0c161`. Canonical owner: `windows_system_proxy.py`. All 18 implementation-PR workflows completed successfully; WinINET Internet Settings backup/restore, registry mutation, per-user proxy-environment persistence/synchronization, WinINET refresh and Windows enable/disable/status/restore-pending implementation now have explicit canonical ownership while the sealed `0.2.3` fail-closed rollback contract remains unchanged. Closure evidence is recorded in `docs/evidence/APL_IP_003_SLICE_8_WINDOWS_SYSTEM_PROXY.md`.
- **DONE — Slice 9:** Recovery Run/autostart ownership and classification extraction. PR `#134`, merge commit `344b97b9aff858fa6abefc59c51be105af4cdf15`. Canonical owner: `recovery_autostart.py`. All 18 implementation-PR workflows completed successfully; exact current/temporary/known-legacy command ownership, foreign Run-entry preservation, legacy portable Run repair, recovery Run enable/disable and fail-closed legacy-process inspection now have explicit canonical ownership while the sealed `0.2.3` recovery safety contract remains unchanged. Closure evidence is recorded in `docs/evidence/APL_IP_003_SLICE_9_RECOVERY_AUTOSTART.md`.
- **DONE — Slice 10:** stale/orphan PAC diagnostics and cleanup ownership extraction. PR `#136`, merge commit `82cec6776306c991b53029ac27e6864235201704`. Canonical owner: `windows_pac_recovery.py`. All 18 implementation-PR workflows completed successfully; stale-system-proxy diagnostics, any-known-backup ambiguity evidence, exact orphaned Arvectum PAC eligibility, durable pre-cleanup snapshots and race-safe deletion of only `AutoConfigURL` now have explicit canonical ownership while the sealed `0.2.3` fail-closed recovery contract remains unchanged. Closure evidence is recorded in `docs/evidence/APL_IP_003_SLICE_10_WINDOWS_PAC_RECOVERY.md`.
- **NEXT — Slice 11:** structured logging bridge ownership extraction from `proxy_core_legacy.py`: canonical construction/ownership of the `StructuredLogger` instance plus `structured_log()` and `_log()` compatibility sink, with exact current app-version/milestone/component metadata and never-raise logging semantics preserved. Platform predicates/runtime identity and GUI autostart remain separate later slices.
- The human/legal rights-basis reference remains a parallel governance gate. Completing engineering slices does not waive it and does not authorize a clean-IP tag.

## Scope

### 1. Canonical identity and repository references

- Add a governed `.mailmap` that maps the owner's historical `arvectum` / `arutyunoveth` Git identities to one canonical Arvectum identity without rewriting Git history.
- Keep `OpenAI <noreply@openai.com>` and automation identities historically truthful; do not remap them to the human author.
- Normalize current repository references to `arvectum/proxy-launcher`.
- Remove obsolete references to old usernames, forks, temporary worktrees, local absolute paths, and superseded repository names from current maintained source/docs where they are not required as historical evidence.
- Preserve legitimate upstream dependency/source URLs where required for licensing, reproducibility, or provenance.

### 2. Source-style normalization

- Establish one naming convention for modules, classes, functions, enums, dataclasses, state objects, diagnostics, errors, and CLI surfaces.
- Normalize typing, docstrings, exception boundaries, logging, structured diagnostics, configuration/state handling, and security-sensitive mutation patterns.
- Remove obsolete patch-history comments and task-number commentary from production source when they no longer explain current behaviour; move durable rationale to architecture/governance docs.
- Rewrite generic/template-like scaffolding into project-specific abstractions where doing so improves clarity and ownership, without semantic churn for its own sake.

### 3. Architecture normalization

Target an explicit Arvectum architecture with these project-wide principles:

1. explicit ownership;
2. fail-closed mutation;
3. deterministic recovery;
4. capability-first platform abstraction;
5. separation of control plane and enforcement plane;
6. immutable/verifiable release and provenance evidence.

Refactor core/recovery/routing/platform modules toward those principles. Reduce historical layering and compatibility seams where tests and supported behaviour prove they are no longer required.

Specific review targets include:

- `proxy_core_legacy.py` and legacy compatibility boundaries;
- control/backend contracts;
- recovery and ownership/state journals;
- Windows/Linux/macOS backend symmetry;
- routing model/control-plane boundaries;
- GUI/CLI use of the common application layer;
- duplicated internal scaffolds identified by APL-IP-001 pre-review.

### 4. Behaviour-preserving migration

Refactor incrementally. Every slice must preserve or deliberately version observable product behaviour.

Required loop:

`baseline tests -> bounded refactor -> targeted tests -> full regression -> package/build contract checks`

No single refactor PR should combine unrelated behavioural features with structural cleanup unless the behaviour change is required to make the architecture coherent and is explicitly documented.

The sealed Windows `0.2.3` release remains the reference baseline and must not be silently replaced or mutated.

### 5. Post-refactor IP baseline

After the canonical refactor is complete:

- select a new exact source candidate;
- regenerate provenance manifest and SBOM evidence;
- repeat OSS/public-similarity and provenance-marker review;
- review changed third-party/runtime payload boundaries;
- perform a bounded human review of the new canonical architecture;
- reconcile the result with the executed author-to-ООО rights instrument;
- create a new clean-IP tag only after the new candidate is explicitly APPROVED.

## Exit criteria

APL-IP-003 is DONE only when all of the following are true:

- maintained source has one coherent Arvectum code/architecture style;
- current source/docs use the canonical `arvectum/proxy-launcher` repository identity except where historical/upstream references are required;
- historical human Git identities are normalized via `.mailmap`, not rewritten;
- AI/bot identities have not been falsified or reassigned;
- obsolete compatibility/duplication is removed or explicitly justified;
- Windows/Linux/macOS regression and applicable packaging checks pass;
- the protected Windows `0.2.3` baseline remains reproducibly identifiable and unchanged;
- a new exact post-refactor IP review candidate is selected;
- post-refactor provenance/human/legal review completes with no unresolved blocker;
- a new clean-IP baseline/tag is created only after explicit APPROVED status.

## Non-goals

- rewriting Git history;
- deleting provenance evidence;
- pretending AI assistance did not occur;
- replacing third-party license notices with Arvectum authorship claims;
- adding Windows per-application production enforcement while the APL-ROUTE-003 STOP-GATE is unresolved;
- using the paused Astra or blocked Windows acceptance environments as prerequisites for purely structural refactor work.
