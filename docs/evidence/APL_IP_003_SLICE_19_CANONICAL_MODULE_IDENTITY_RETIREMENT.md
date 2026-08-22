# APL-IP-003 Slice 19 — canonical module-identity retirement

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-22

## Purpose

Retire the final compatibility module-identity boundary after Slices 12–18 removed all maintained implementation and standard-library aliases from `proxy_core_legacy.py`.

The slice preserves the sealed Windows `0.2.3` behavior contract while making `proxy_core.py` itself the single canonical mutable composition object.

## Baseline and merge

- pre-slice protected `main`: `8d9b3d24d8d6f1afa4f763795784b392c0aa3f4f`
- implementation PR: `#154`
- final reviewed implementation head: `61412c665597611d27dd7048fbcb1da2af6e28bc`
- implementation merge: `235a92d27405cae09783258c0cb0c5e86a8921f1`
- product version: `0.2.3` unchanged

## Pre-slice identity boundary

At Slice 19 entry, `proxy_core_legacy.py` contained no maintained runtime implementation and no standard-library compatibility aliases. It held only release/state/install bootstrap values. `proxy_core.py` imported that module as `_core`, installed canonical owners onto it, and finally replaced its own import entry with:

```python
_runtime_sys.modules[__name__] = _core
```

That shape had become historical construction debt rather than a runtime-implementation boundary.

## Canonical composition result

Slice 19:

1. moves the exact bootstrap values into `proxy_core.py` before owner configuration;
2. resolves `_core` as the real canonical module object using `sys.modules[__name__]` only for lookup, not replacement;
3. keeps owner configuration/install order unchanged;
4. removes `sys.modules[__name__] = _core`;
5. physically deletes `proxy_core_legacy.py`;
6. replaces the legacy-shell regression with `tests/test_canonical_core_composition.py`;
7. adds repository-wide AST evidence that no live Python source imports `proxy_core_legacy`;
8. updates canonical-source and backend CI compile manifests so deleted compatibility files/tests are no longer operational dependencies.

After the slice:

- `import proxy_core` returns a module whose canonical name is `proxy_core`;
- its file identity is `proxy_core.py`;
- no `proxy_core_legacy.py` exists in the maintained tree;
- no source imports `proxy_core_legacy`;
- no `sys.modules` self-replacement exists;
- every installed runtime callable is still owned by an explicit canonical module;
- all 13 historical `core.<stdlib>` aliases remain absent.

## CI-discovered stale construction references

The first implementation head proved that two CI manifests still treated the deleted shell as source:

- `.github/workflows/core-backends.yml`
- `.github/workflows/apl-ip-003-canonical-source.yml`

Both initially failed in their compile steps because `proxy_core_legacy.py` no longer existed. No runtime test had failed.

The final implementation migrated those manifests to `proxy_core.py` plus `tests/test_canonical_core_composition.py`. This is recorded as positive evidence that the compatibility boundary was removed from operational tooling as well as Python runtime code.

## Final implementation evidence

Final head `61412c665597611d27dd7048fbcb1da2af6e28bc` completed all **18/18 triggered workflows successfully**:

- APL-IP-003 canonical source — Windows/macOS/Ubuntu;
- Core backend contract — Ubuntu/macOS;
- Windows P0 portable;
- Windows installer;
- APL-IP-002-WIN controlled offline build;
- Phase 5 Config and Security;
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

- **623 tests passed**;
- PyInstaller portable build succeeded;
- product version remained `0.2.3`;
- Documents execution smoke passed;
- packaged Doctor smoke passed.

Installer evidence:

- pinned Inno Setup 6.7.1 installed and validated;
- portable baseline and final EXE metadata passed;
- predecessor lifecycle fixture passed;
- canonical installer compilation passed;
- fresh / upgrade / repair / uninstall E2E passed;
- Gate R6 acceptance matrix passed.

Controlled-offline evidence:

- contract tests passed;
- official CPython base was Sigstore-verified;
- exact CPython 3.12 Windows wheelhouse was acquired and verified;
- controlled archive contract passed;
- canonical portable build succeeded from verified offline inputs;
- no package-index fallback was proven.

## Behavior and governance boundaries

Slice 19 does **not**:

- change version `0.2.3`;
- change canonical owner implementation logic;
- weaken network rollback, recovery, routing or foreign-proxy ownership rules;
- rewrite Git history or provenance;
- claim final clean-IP approval.

The named author-to-ООО rights-basis execution reference remains **HUMAN/LEGAL PENDING**. Automated engineering evidence cannot waive that gate or authorize a clean-IP tag.

## Next bounded work

`APL-IP-003 Slice 20 — maintained-source patch-history & canonical terminology normalization`.

The next slice removes obsolete APL-IP-003 slice/task narration and now-false compatibility/"later extraction" language from maintained production docstrings/comments, replaces it with durable architectural descriptions, and adds a source-hygiene guard. Behavioral `legacy` terminology that denotes real compatibility data, migration, recovery ownership or historical release formats remains untouched.
