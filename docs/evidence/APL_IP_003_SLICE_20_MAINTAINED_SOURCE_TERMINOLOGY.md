# APL-IP-003 Slice 20 — maintained-source terminology normalization

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-22

## Purpose

Normalize maintained canonical production source so it describes the current Arvectum architecture rather than the bounded migration history that produced it.

The slice is source-hygiene only. It does not alter control flow, state, routing, recovery, networking or packaging behavior and preserves the sealed Windows `0.2.3` baseline.

## Baseline and merge

- pre-slice protected `main`: `50d5432a0411c729a12968801d60fee4e2578398`
- implementation PR: `#156`
- final reviewed implementation head: `c5ced62ef22bf89cea7805ad4929a3667d4d43f8`
- implementation merge: `249886a8914f78b769980458621fa33b7b86dc27`
- product version: `0.2.3` unchanged

## Normalized maintained source

The following thirteen canonical production modules now use durable current-architecture ownership descriptions instead of APL-IP-003 slice/task narration and already-completed future-extraction language:

- `proxy_core.py`
- `application_filesystem.py`
- `portable_lifecycle.py`
- `configuration_storage.py`
- `routing_policy.py`
- `local_proxy_transport.py`
- `process_supervision.py`
- `application_runtime.py`
- `windows_system_proxy.py`
- `recovery_autostart.py`
- `windows_pac_recovery.py`
- `logging_bridge.py`
- `system_proxy_runtime.py`

Module docstrings now describe present ownership and boundaries. Configured owners use one current term for their mutable dependency boundary: the canonical composition module.

Behavioral uses of `legacy` were deliberately preserved where they identify real data or compatibility contracts, including state migration, recovery ownership, release formats and historical installer forms.

## Deterministic source-only transformation

To keep this broad text normalization mechanically bounded, the branch used a one-shot GitHub Actions transformation that:

1. parsed each target source module with Python AST;
2. replaced only the module docstring and `configure()` docstring at known AST locations;
3. re-parsed every transformed source file;
4. compiled all target modules;
5. rejected whitespace errors with `git diff --check`;
6. committed the normalized source under the explicit `Arvectum Automation` identity;
7. removed the one-shot workflow from the branch before review.

The one-shot workflow is therefore absent from the final implementation PR tree and does not become a maintained build dependency.

## Permanent source-hygiene guard

`tests/test_source_hygiene.py` now protects the maintained canonical source set.

It rejects reintroduction of obsolete refactor-history terms such as:

- `APL-IP-003` in production source;
- `proxy_core_legacy`;
- `outside this slice`;
- `later bounded`;
- `extracted independently later`.

It also requires current canonical ownership docstrings and one composition-binding term across configured owners.

The guard is compiled and executed by `.github/workflows/apl-ip-003-canonical-source.yml` on Windows, macOS and Ubuntu.

## Final implementation evidence

Final head `c5ced62ef22bf89cea7805ad4929a3667d4d43f8` completed all **18/18 triggered workflows successfully**:

- APL-IP-003 canonical source — Windows/macOS/Ubuntu;
- Core backend contract;
- Phase 5 Config and Security;
- Windows P0 portable;
- Windows installer;
- APL-IP-002-WIN controlled offline build;
- macOS packaging;
- Debian package;
- AppImage;
- Linux diagnostics support bundle;
- Doctor;
- structured logging + secret redaction;
- Windows diagnostics + privacy;
- SAST;
- Secret scan;
- Dependency vulnerability scan;
- SBOM;
- APL-IP-001 provenance.

Windows clean-build evidence:

- **626 tests passed**;
- the three new maintained-source hygiene tests passed;
- PyInstaller portable build succeeded;
- product version remained `0.2.3`;
- Documents execution smoke passed;
- packaged Doctor smoke passed.

Installer evidence:

- pinned Inno Setup 6.7.1 validation passed;
- canonical installer compilation passed;
- fresh / upgrade / repair / uninstall E2E passed;
- Gate R6 acceptance matrix passed.

Controlled-offline evidence:

- official CPython base was Sigstore-verified;
- exact CPython 3.12 Windows wheelhouse was verified;
- canonical portable build succeeded from controlled offline inputs;
- no package-index fallback was proven.

## Behavior and governance boundaries

Slice 20 does **not**:

- change application behavior or version `0.2.3`;
- remove genuine historical/legacy compatibility semantics;
- rewrite Git history, commit identities or provenance;
- claim final clean-IP approval.

The named author-to-ООО rights-basis execution reference remains **HUMAN/LEGAL PENDING**. Automated engineering evidence cannot waive that gate or authorize a clean-IP tag.

## Next bounded work

`APL-IP-003 Slice 21 — regression naming & repository hygiene`.

The next slice removes obsolete slice-number prefixes from maintained regression test names, canonicalizes stale current-repository references while preserving historical evidence and `.mailmap`, and adds guards preventing both forms of maintenance debt from returning.
