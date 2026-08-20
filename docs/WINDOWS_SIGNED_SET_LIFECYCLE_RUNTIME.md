# Windows signed-set lifecycle runtime handling

Task: `APL-REL-014`

This layer exists only for a real owner Windows host where the exact governed installer copy may already be running when lifecycle acceptance starts.

Canonical runtime-aware wrapper:

`tools/windows_signed_set_lifecycle_acceptance_runtime.ps1`

It does not replace the established lifecycle or owner-host snapshot contracts. Instead it performs a narrow outer sequence:

1. require the exact HKCU installer registration;
2. require the exact sealed 0.2.3 application hash, cached installer hash, manifest/version and install location;
3. enumerate every running `Arvectum Proxy Launcher.exe` process;
4. fail closed if any same-named process has an unverifiable or foreign executable path;
5. classify the governed processes as proxy-core (`--start`) or GUI and remember the original running shape;
6. use the product `--stop` path first so core shutdown and Windows proxy rollback use the application's governed recovery behavior;
7. if necessary, use explicit `--rollback` and require recovery evidence to clear;
8. close/terminate only processes whose executable path is exactly the validated governed installed EXE;
9. delegate to `windows_signed_set_lifecycle_acceptance_owner_host.ps1` for the reversible install/state/registry/shortcut snapshot and exact signed-set lifecycle acceptance;
10. after the owner-host snapshot is restored, restart proxy-core and/or GUI only if they were running before acceptance;
11. extend lifecycle evidence with runtime quiesce/restore fields.

Required final runtime evidence when a running instance existed:

- `owner_host_runtime_was_running = true`
- `owner_host_runtime_quiesced = PASS`
- `owner_host_runtime_restored = true`
- `owner_host_core_was_running` records the original headless core state
- `owner_host_gui_was_running` records the original GUI state
- overall lifecycle `result = PASS`

The signed release directory is never modified by this runtime wrapper.
