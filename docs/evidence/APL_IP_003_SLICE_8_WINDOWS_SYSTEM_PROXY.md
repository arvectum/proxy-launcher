# APL-IP-003 Slice 8 — Windows WinINET / proxy-environment persistence and system-proxy ownership extraction evidence

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Canonical merge

- Pull request: `#132` — `APL-IP-003 Slice 8 — Windows system-proxy ownership extraction`
- Merge commit: `cd1f032c1505e3123779b1ac0f283513fce0c161`
- Pre-slice main baseline: `c87b94a475f005a3feae67d111dc81c380f14965`
- Reviewed final PR head: `4e78461a2b965210eab8612d533dca40bc4eea2c`
- Product version: unchanged (`0.2.3`)
- The final self-review restored the pre-existing Windows backend diagnostic text before the final gate run; the evidence below applies to the exact reviewed head above.

## Extracted ownership

`windows_system_proxy.py` is now the canonical Windows WinINET / per-user proxy-environment implementation owner, installed through the established mutable `proxy_core` compatibility seam before `system_proxy_runtime` captures its Windows adapter, for:

- `_env_backup_path` and `_internet_backup_path` runtime evidence paths;
- `_read_internet_settings` for the owned HKCU WinINET value set;
- `_valid_internet_backup`, `_known_internet_backup_paths`, and `_valid_internet_backup_at`;
- `_exact_arvectum_pac_url` structural PAC ownership comparison;
- `_save_internet_backup` and `_restore_internet_backup`;
- `_read_user_env`, `_write_user_env`, and `_delete_user_env` for HKCU user environment state;
- `_broadcast_environment_change`;
- `_combined_no_proxy`, `_enable_client_proxy_env`, `sync_client_no_proxy`, and `_disable_client_proxy_env`;
- `pac_url`;
- `_reg_set` and `_reg_del` Internet Settings mutation primitives;
- `_refresh_internet` WinINET settings-change/refresh notification;
- the Windows implementations of `enable_system_proxy`, `disable_system_proxy`, `system_proxy_enabled`, and `network_restore_pending` captured by `system_proxy_runtime.WindowsCoreAdapter`.

The public application-facing system-proxy seams remain owned by `system_proxy_runtime.py`, which preserves backend selection, operational gates, fail-closed exception handling and cross-platform composition while delegating the Windows implementation to the canonical Slice 8 owner.

## Deliberately retained outside Slice 8

The following ownership-sensitive recovery responsibilities remain in `proxy_core_legacy.py` for later bounded extraction:

- Recovery Run/autostart command ownership classification and mutation;
- exact current/temporary/known-legacy recovery command recognition;
- recovery Run-entry enable/repair/disable behaviour;
- stale system-proxy diagnostics;
- orphaned Arvectum PAC detection, snapshotting and cleanup;
- `_any_known_internet_backup_exists` where it participates in orphan-PAC safety decisions.

This separation prevents WinINET/env persistence extraction from being combined with destructive recovery-ownership changes in one review surface.

## Behaviour contract preserved

The sealed Windows `0.2.3` network mutation and rollback behaviour remains the reference contract. Slice 8 preserves, without intentional product change:

- original Internet Settings are snapshotted before any WinINET mutation;
- an existing valid Internet Settings backup is reused rather than replaced;
- an existing invalid backup is never overwritten and blocks new mutation;
- failure to obtain a complete registry snapshot blocks proxy enable before registry/env/Run mutation;
- a missing or invalid Internet Settings backup never authorizes guessed destructive cleanup and therefore leaves WinINET values unchanged;
- valid restore returns every captured Internet Settings value to its exact prior present/absent state and keeps the backup if restoration is incomplete;
- PAC ownership is structural and exact: scheme, loopback host, configured port/path, and absence of query/fragment/user-info must match;
- `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and `NO_PROXY` are snapshotted before per-user proxy-environment mutation;
- an invalid existing proxy-environment backup blocks mutation rather than replacing user evidence;
- Arvectum's active `NO_PROXY` combines the user's original entries with built-in and current governed bypass policy without discarding the original user entries;
- incomplete user-environment restoration keeps its backup for retry and does not broadcast a false successful restore;
- enabling the Windows proxy still uses PAC plus `ProxyEnable=0`, then user proxy environment, then the existing recovery-autostart collaborator;
- partial enable still rolls back Internet Settings, proxy environment and recovery-autostart state and refreshes WinINET;
- recovery Run ownership is removed during disable only after the owned PAC is inactive and user proxy-environment rollback is safe or no longer pending;
- disable still re-checks active PAC state after WinINET refresh and never reports success while the owned PAC remains active;
- `network_restore_pending` remains driven by retained Internet Settings or proxy-environment rollback evidence;
- non-Windows behaviour through the public composition layer remains unchanged.

## Compatibility boundary

`proxy_core.py` installs `windows_system_proxy` after the already extracted filesystem/configuration/routing/transport/process owners and before configuring `system_proxy_runtime`. Consequently `system_proxy_runtime._WINDOWS_CORE` captures the canonical Windows functions, after which the public `proxy_core` system-proxy functions are intentionally rewired to the composition layer.

Internal calls in `windows_system_proxy.py` resolve collaborators dynamically through the same mutable `proxy_core` module object. Existing monkeypatch seams therefore continue to work for prior Windows recovery and foreign-proxy tests while executable ownership is explicit.

`proxy_core_legacy.py` was not edited in Slice 8. Historical source remains truthful provenance evidence rather than being deleted or rewritten to manufacture a cleaner history.

## Targeted regression coverage

`tests/test_windows_system_proxy.py` adds bounded checks for:

- canonical ownership of WinINET/env persistence helpers;
- canonical Windows implementation capture by `system_proxy_runtime` while public seams remain composition-owned;
- structural PAC ownership and rejection of misleading variants;
- refusal to overwrite an invalid Internet Settings backup;
- durable Internet Settings snapshot and exact restore/delete semantics;
- missing/invalid backup non-destructive restore behaviour;
- proxy-environment snapshot plus original `NO_PROXY` preservation;
- refusal to mutate over an invalid proxy-environment backup;
- retained retry evidence after incomplete environment restore;
- enable fail-fast before mutation when backup cannot be proven;
- full rollback path after partial enable failure;
- retention of recovery-autostart ownership while network rollback is unsafe;
- restore-pending semantics for Slice 8 evidence.

The APL-IP-003 canonical-source workflow was extended to compile `windows_system_proxy.py` and `windows_backend.py` and to run the new Slice 8 suite plus the established canonical refactor, process-supervision, application-runtime and Windows-backend tests on Ubuntu, macOS and Windows.

## Independent regression evidence

The pre-existing regression suites were not rewritten around the extraction. On the exact reviewed PR head:

- `APL-IP-003 canonical source` completed successfully across its Ubuntu/macOS/Windows matrix;
- `Phase 5 Config and Security` completed successfully, independently exercising the established configuration/network/recovery surface;
- `Core backend contract` completed successfully;
- the existing foreign-proxy protection suite therefore continued to enforce exact PAC ownership and non-destructive missing/invalid-backup recovery through the installed `proxy_core` facade;
- Windows portable and installer gates completed successfully against the extracted implementation.

## Implementation PR workflow evidence — 18/18 SUCCESS

- `32491946995` — APL-DIAG-003/006 Windows diagnostics + privacy
- `32491946941` — SBOM
- `32491946950` — APL-LNX-006 Linux diagnostics support bundle
- `32491946934` — macOS packaging
- `32491946935` — Core backend contract
- `32491946911` — Dependency vulnerability scan
- `32491946930` — APL-DIAG-001/002 structured logging + secret redaction
- `32491946894` — Phase 5 Config and Security
- `32491946928` — APL-IP-003 canonical source
- `32491946994` — Windows installer
- `32491946939` — APL-LNX-008 AppImage
- `32491947032` — APL-IP-001 provenance
- `32491946903` — APL-IP-002-WIN controlled offline build
- `32491946951` — APL-LNX-007 Debian package
- `32491946931` — SAST
- `32491946924` — APL-DIAG-004 Doctor
- `32491946952` — Windows P0 portable
- `32491946964` — Secret scan

## Release / packaging evidence

- Canonical-source compile + targeted regression: Ubuntu, macOS and Windows — SUCCESS.
- Full Phase 5 configuration/security regression — SUCCESS.
- Core backend contract — SUCCESS.
- Windows P0 portable canonical build/smoke gate — SUCCESS.
- Windows installer build/E2E gate — SUCCESS.
- Controlled offline Windows build — SUCCESS.
- macOS package, Debian package and AppImage package gates — SUCCESS.
- SAST, dependency vulnerability, secret scan, provenance, SBOM and diagnostics gates — SUCCESS.

## Governance

This is an engineering ownership/refactor completion only. It does not declare the repository clean-IP APPROVED and does not authorize a clean-IP tag. The APL-IP-001 author-to-ООО rights-basis execution remains HUMAN/LEGAL PENDING and must be reconciled during the post-refactor IP baseline process.

Git history and AI/automation provenance have not been rewritten or reassigned.

## Next bounded slice

**APL-IP-003 Slice 9 — Recovery Run/autostart ownership and classification extraction.**

Planned bounded ownership: exact recovery command classification for current, proven temporary and known legacy commands; foreign Run-entry preservation; recovery-autostart enable/repair/disable mutation; and supporting ownership/path helpers currently retained in `proxy_core_legacy.py`.

Stale/orphan PAC diagnostics and cleanup remain a separate later slice so destructive cleanup can be reviewed independently from Run-entry ownership.
