# APL-IP-003 Slice 22 — application/backend boundary & production-source history cleanup

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-22

## Scope

Slice 22 performed the final bounded audit and cleanup of the application/platform boundary outside the canonical-owner modules already normalized in earlier APL-IP-003 slices. The slice was intentionally guard-first: it did not assume that GUI/backend layering needed redesign, and it did not change product features, network mutation semantics, recovery semantics, packaging behavior, or the sealed `0.2.3` baseline.

## Baseline

Protected `main` before Slice 22 implementation was the Slice 21 closure merge:

- `5c0c6999446258f54e77fc3d5f2a58b858ccf4ff`

## Guard-first authoritative inventory

`tests/test_application_boundary_hygiene.py` was introduced first and the initial canonical-source run was intentionally allowed to act as an inventory probe.

The probe established three facts:

1. **GUI layering was already structurally correct.** `proxy_gui.py` and `linux_gui.py` did not import concrete `windows_backend`, `linux_backend`, `macos_backend`, `windows_system_proxy`, `windows_pac_recovery`, or `system_proxy_runtime` implementations directly. Concrete backend selection remained owned by `backend_runtime.create_backend()`.
2. **Production refactor-history narration remained in 29 root/current production Python files.** These were docstring/comment references to historical `APL-*` engineering task IDs rather than present-tense architecture ownership.
3. **Stale internal boundary vocabulary had exactly four Python consumers.** `legacy_core`, `_resolved_legacy_config`, and `_config_matches_legacy_runtime` occurred only in `backend_runtime.py`, `system_proxy_runtime.py`, `windows_backend.py`, and `tests/test_backend_runtime.py`.

Because the GUI/application boundary was already sound, the slice deliberately avoided a needless runtime redesign.

## Implemented cleanup

The bounded normalization removed engineering-task IDs and slice narration from maintained production docstrings/comments while preserving real legacy/recovery-format terminology that describes supported historical data or migration behavior.

Internal Windows backend terminology was normalized end-to-end:

- `legacy_core` -> `runtime_core`;
- `_resolved_legacy_config` -> `_resolved_runtime_config`;
- `_config_matches_legacy_runtime` -> `_config_matches_runtime`.

The rename propagated through the actual composition path:

`system_proxy_runtime -> backend_runtime.create_backend(runtime_core=...) -> WindowsBackend(runtime_core=...)`.

Repository-wide AST evidence proved these names were internal-only before retirement; no compatibility alias was retained for an unproven consumer.

The permanent guard now enforces:

- no `APL-*` engineering task IDs in maintained production docstrings/comments;
- no `Slice N` refactor narration in maintained production docstrings/comments;
- GUI entry points do not import concrete backend implementations directly;
- `backend_runtime` remains the concrete-backend selection owner;
- the retired internal boundary identifiers have no live Python consumers.

## Review correction

The deterministic normalization helper used the truthful automation identity `Arvectum Automation <automation@arvectum.com>` and self-deleted after applying the bounded inventory transformation. Human-owner review then corrected two mechanically awkward descriptions in `backend_runtime.py` and `windows_backend.py`; the final PR head is therefore an owner-reviewed source tree rather than an unreviewed mechanical rewrite.

No historical commits or authorship identities were rewritten or reassigned.

## Implementation PR and merge

Implementation PR:

- PR `#161` — `APL-IP-003 Slice 22 — application/backend boundary & production-source history cleanup`;
- final implementation head: `6307726bf20f05c9955704239ada942b96bd225a`;
- implementation merge: `8a75383a0bca5979c3953de01d7ffcc903384553`.

## Final CI evidence

The final implementation head completed **20/20 triggered workflows successfully**.

### Canonical/application boundary

- APL-IP-003 canonical source: Windows **SUCCESS**;
- APL-IP-003 canonical source: macOS **SUCCESS**;
- APL-IP-003 canonical source: Ubuntu **SUCCESS**;
- Core backend contract: **SUCCESS**.

### Windows behavioral and release baseline

- Windows P0 portable: **SUCCESS**;
- full Windows unit suite: **634 tests, OK**;
- product version: **0.2.3 unchanged**;
- PyInstaller portable build and PE metadata verification: **SUCCESS**;
- Documents canonical-copy execution smoke: **SUCCESS**;
- packaged Doctor smoke: **SUCCESS**;
- Windows installer: **SUCCESS**;
- pinned Inno Setup / sovereignty checks: **SUCCESS**;
- fresh / upgrade / repair / uninstall E2E: **SUCCESS**;
- Gate R6 acceptance matrix: **SUCCESS**.

### Controlled/offline build

- APL-IP-002-WIN controlled offline build: **SUCCESS**;
- official CPython base Sigstore verification: **SUCCESS**;
- exact CPython 3.12 Windows wheelhouse acquisition: **SUCCESS**;
- offline canonical portable build from verified CPython + wheelhouse: **SUCCESS**;
- explicit proof of no package-index fallback in offline build phase: **SUCCESS**.

### macOS / Linux platform symmetry

- macOS packaging — Apple Silicon: tests, `.app`, DMG build/inspection: **SUCCESS**;
- macOS packaging — Intel: tests, `.app`, DMG build/inspection: **SUCCESS**;
- Debian package: **SUCCESS**;
- AppImage: **SUCCESS**;
- Debian/Ubuntu acceptance: **SUCCESS**;
- Linux diagnostics support bundle: **SUCCESS**.

### Diagnostics / security / provenance

- Doctor: **SUCCESS**;
- structured logging + secret redaction: **SUCCESS**;
- Windows diagnostics + privacy: **SUCCESS**;
- Windows routing prototype: **SUCCESS**;
- Phase 5 Config and Security: **SUCCESS**;
- APL-IP-001 provenance: **SUCCESS**;
- SAST: **SUCCESS**;
- dependency vulnerability scan: **SUCCESS**;
- SBOM: **SUCCESS**;
- secret scan: **SUCCESS**.

## Final result

- GUI -> concrete-backend direct-import violations: **0**;
- backend selection owner: **`backend_runtime` retained and guarded**;
- maintained production `APL-*` task-history narration: **29 files -> 0**;
- maintained production `Slice N` refactor narration: **0**;
- retired stale internal boundary identifiers: **0 live Python consumers**;
- sealed application version: **0.2.3 unchanged**;
- runtime/network/recovery behavior: **unchanged**;
- Git history/provenance: **preserved**;
- human/automation identity history: **not falsified**.

## Governance boundary

Slice 22 completes this bounded engineering cleanup but does not constitute legal approval of a post-refactor clean-IP baseline. The author-to-ООО rights-basis execution reference and final human/legal review remain separate mandatory gates. No clean-IP `APPROVED` status or tag is authorized by this evidence.

## Next bounded slice

**APL-IP-003 Slice 23 — engineering completion audit & post-refactor candidate selection.**

Perform a repository-wide final audit against the APL-IP-003 engineering exit criteria; verify that no canonical-source, repository-identity, legacy-module, stdlib-facade, regression-naming, application/backend-boundary, platform-packaging, recovery-safety, or provenance engineering debt remains; select the exact post-refactor candidate SHA; and record engineering completion without misrepresenting the still-pending human/legal clean-IP approval gate.
