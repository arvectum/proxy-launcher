# APL-IP-003 Slice 9 — Recovery Run/autostart ownership and classification extraction evidence

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Canonical merge

- Pull request: `#134` — `APL-IP-003 Slice 9 — recovery autostart ownership extraction`
- Merge commit: `344b97b9aff858fa6abefc59c51be105af4cdf15`
- Pre-slice main baseline: `95cc865b3f1101c09e74bb0d83c58d66f85b526e`
- Reviewed final PR head: `55f4494766ee56113eaeb1d112550bb7af8fec74`
- Product version: unchanged (`0.2.3`)
- No implementation commit was added after PR review began; the workflow evidence below applies to the exact reviewed head above.

## Extracted ownership

`recovery_autostart.py` is now the canonical Recovery Run/autostart ownership and classification owner, installed through the established mutable `proxy_core` compatibility seam before the Windows system-proxy implementation is wired, for:

- `_self_start_command` — exact current launcher start command;
- `_normalize_command` — bounded quoting/whitespace normalization used for exact comparisons;
- `_known_legacy_recovery_dirs` — explicit historical directory evidence;
- `_recovery_command_target` — quoted target/argument parsing without substring heuristics;
- `_is_temporary_arvectum_start` — strict temporary launcher `--start` recognition;
- `_is_proven_legacy_arvectum_start` — exact proven legacy launcher-start recognition;
- `_delete_run_value` — HKCU Run deletion primitive;
- `repair_portable_run_entries` — ownership-sensitive migration of legacy user/recovery Run entries;
- `classify_recovery_autostart` — `CURRENT_OWNED` / `LEGACY_ARVECTUM` / `FOREIGN` / `MISSING` classification;
- `is_owned_arvectum_start_command` — strict shared launcher-start ownership predicate also consumed by the GUI/user-autostart safety layer;
- `_recovery_legacy_process_active` — fail-closed exact legacy process inspection;
- `_get_recovery_run_value` and `_set_recovery_run_value` — recovery Run value accessors;
- `_enable_recovery_autostart` and `_disable_recovery_autostart` — sealed P0 recovery Run compatibility mutation.

The corresponding recovery constants retain their exact sealed values:

- `_RECOVERY_RUN_VALUE = "ArvectumProxyLauncherRecovery"`;
- `_RECOVERY_CURRENT_OWNED = "CURRENT_OWNED"`;
- `_RECOVERY_LEGACY_ARVECTUM = "LEGACY_ARVECTUM"`;
- `_RECOVERY_FOREIGN = "FOREIGN"`;
- `_RECOVERY_MISSING = "MISSING"`.

## Deliberately retained outside Slice 9

The following responsibilities remain outside this bounded ownership extraction:

- stale system-proxy diagnostics;
- orphaned Arvectum PAC eligibility detection;
- known Internet-backup evidence checks used specifically by orphan-PAC safety decisions;
- durable orphan-PAC snapshotting;
- race-safe orphan `AutoConfigURL` cleanup;
- GUI/Task Scheduler implementation of ordinary user-autostart UX.

The GUI can consume the canonical strict `is_owned_arvectum_start_command` predicate without transferring GUI/Task Scheduler implementation ownership into this slice.

## Behaviour contract preserved

The sealed Windows `0.2.3` recovery/autostart behaviour remains the reference contract. Slice 9 preserves, without intentional product change:

- command ownership is never inferred from a substring match;
- recovery command parsing requires an explicitly quoted target;
- current ownership requires exact normalized equality with the current launcher start command;
- temporary ownership requires the exact launcher executable name, exact `--start` arguments and a proven temporary root;
- legacy launcher ownership requires the exact launcher executable name and exact `--start` arguments plus explicit temporary/known-legacy/release-directory evidence;
- historical `restore_network.bat` is accepted only as recovery classification evidence when it is the exact target in a known legacy directory and has no arguments;
- `restore_network.bat` does not become an owned launcher-start command for GUI/user-autostart purposes;
- a foreign same-named recovery Run value is never overwritten or deleted;
- an unreadable recovery Run value does not authorize destructive mutation and does not block P0 startup;
- a missing recovery Run value remains a successful no-op;
- current/proven-legacy recovery Run values retain the sealed P0 behavior of being removed because P0 uses the canonical single user-autostart mechanism;
- disable removes only the exact current recovery command or a proven temporary Arvectum launcher start and leaves every other command untouched;
- `repair_portable_run_entries` rewrites the ordinary user-autostart entry only when its old command is proven legacy Arvectum ownership and deletes the recovery entry only under the same proof;
- foreign user/recovery Run entries survive portable repair unchanged;
- process-inspection failure remains fail-closed and therefore blocks treating a potentially active legacy owner as inactive;
- the process-inspection subprocess seam remains dynamically reachable through the mutable `proxy_core` module for existing regression monkeypatches;
- non-Windows recovery-autostart mutation behavior remains a successful no-op.

## Composition boundary

`proxy_core.py` installs `recovery_autostart` after the already extracted filesystem/configuration/routing/transport/process owners and before `windows_system_proxy`. Consequently the Windows system-proxy enable/rollback paths dynamically resolve `_enable_recovery_autostart` / `_disable_recovery_autostart` through the canonical Slice 9 owner.

The module resolves collaborators through the same mutable `proxy_core` object, including `managed_executable`, temporary-path detection, logging and the established `subprocess` seam. Existing tests and downstream components therefore keep the pre-refactor monkeypatch contract while executable ownership moves out of historical storage.

`proxy_core_legacy.py` was not edited in Slice 9. Historical source remains truthful provenance evidence rather than being removed or rewritten to manufacture a cleaner history.

## Targeted regression coverage

`tests/test_recovery_autostart.py` adds bounded checks for:

- canonical source ownership of every extracted Slice 9 function;
- exact preservation of recovery classification constants;
- quoted-target parser requirements;
- exact temporary-start recognition and rejection of misleading filename/argument variants;
- strict current, legacy, historical release-directory and `restore_network.bat` classification;
- rejection of substring, wrong-argument and foreign-path ownership candidates;
- recovery enable deletion only for current/proven-legacy values;
- non-destructive behavior for foreign, unreadable and missing recovery Run state;
- disable deletion only for current/proven-temporary commands;
- owned-only portable Run repair and preservation of foreign entries;
- fail-closed process-inspection failure through the existing `core.subprocess` seam;
- missing legacy executable handling.

The APL-IP-003 canonical-source workflow was extended to compile `recovery_autostart.py` and run the new Slice 9 suite with the established canonical refactor, process-supervision, application-runtime, Windows-system-proxy and Windows-backend suites on Ubuntu, macOS and Windows.

## Independent full-suite evidence

The pre-existing recovery/autostart tests were not rewritten around the extraction. `Phase 5 Config and Security` completed successfully and runs the full `python -m unittest discover -s tests -v` suite on Ubuntu and Windows. It therefore independently exercised the established `test_proxy_core`, foreign-proxy protection, GUI autostart-safety, recovery ownership/state/idempotency and related tests through the installed `proxy_core` facade.

This is separate from the new targeted ownership tests and provides regression evidence that Slice 9 did not require weakening old safety assertions.

## Implementation PR workflow evidence — 18/18 SUCCESS

- `32493469235` — APL-DIAG-003/006 Windows diagnostics + privacy
- `32493469219` — SBOM
- `32493469240` — APL-LNX-006 Linux diagnostics support bundle
- `32493469233` — macOS packaging
- `32493469371` — Core backend contract
- `32493469212` — Dependency vulnerability scan
- `32493469180` — APL-DIAG-001/002 structured logging + secret redaction
- `32493469309` — Phase 5 Config and Security
- `32493469203` — APL-IP-003 canonical source
- `32493469246` — Windows installer
- `32493469146` — APL-LNX-008 AppImage
- `32493469160` — APL-IP-001 provenance
- `32493469164` — APL-IP-002-WIN controlled offline build
- `32493469184` — APL-LNX-007 Debian package
- `32493469195` — SAST
- `32493469162` — APL-DIAG-004 Doctor
- `32493469263` — Windows P0 portable
- `32493469149` — Secret scan

## Release / packaging evidence

- Canonical-source compile + targeted regression: Ubuntu, macOS and Windows — SUCCESS.
- Full Phase 5 unit regression: Ubuntu and Windows — SUCCESS.
- Core backend contract — SUCCESS.
- Windows P0 portable canonical build/smoke gate — SUCCESS.
- Windows installer build/E2E gate — SUCCESS.
- Controlled offline Windows build — SUCCESS, including verified CPython/wheelhouse acquisition, offline canonical portable build and explicit no-package-index-fallback proof.
- macOS package, Debian package and AppImage package gates — SUCCESS.
- SAST, dependency vulnerability, secret scan, provenance, SBOM and diagnostics gates — SUCCESS.

## Governance

This is an engineering ownership/refactor completion only. It does not declare the repository clean-IP APPROVED and does not authorize a clean-IP tag. The APL-IP-001 author-to-ООО rights-basis execution remains HUMAN/LEGAL PENDING and must be reconciled during the post-refactor IP baseline process.

Git history and AI/automation provenance have not been rewritten or reassigned.

## Next bounded slice

**APL-IP-003 Slice 10 — stale/orphan PAC diagnostics and cleanup ownership extraction.**

Planned bounded ownership: stale system-proxy detection; exact orphaned-Arvectum-PAC eligibility; known Internet-backup evidence checks used by that decision; durable orphan-state snapshotting; registry-race revalidation; deletion of only the exact owned `AutoConfigURL`; WinINET refresh and post-cleanup verification through the already canonical Windows system-proxy seams.

Ambiguous ownership, active listener/process evidence, retained backup evidence or a registry race must remain non-destructive terminal conditions rather than authorizing cleanup.
