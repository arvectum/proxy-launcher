# APL-IP-003 — Arvectum canonical source refactor

Status: **ACTIVE — SLICES 1–2 MERGED; FINAL CLEAN-IP APPROVAL STILL HUMAN/LEGAL GATED**

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
- **NEXT — Slice 3:** configuration loading/validation, atomic persistence and configuration-recovery ownership extraction from `proxy_core_legacy.py`, preserving the established config/security contract and `0.2.3` behaviour.
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