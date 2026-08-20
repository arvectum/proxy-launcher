# Windows signed-set lifecycle acceptance

Task: `APL-REL-014`

This gate proves the real lifecycle behavior of the exact Russian production release already approved by `APL-REL-013`.

Pinned release identity:

- version: `0.2.3`
- tag: `v0.2.3-ru.2`
- release-policy commit: `47823585c42da54ab51dc2246583dc24d74d4ba6`
- portable ZIP SHA-256: `62d313547b4d8c2c8e6951d6cd866bb954fdf199ad7650063c8ed3bfbc455801`
- installer SHA-256: `5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414`
- governed signer thumbprint: `EE1CFA955BA22F03C39C76B183D94CD37494582E`
- production gate: `PUBLISH`

Canonical script:

`tools/windows_signed_set_lifecycle_acceptance.ps1`

## Mandatory environment boundary

**Do not run this destructive lifecycle gate on a normal owner workstation.**

A real owner-host attempt on 2026-08-20 successfully restored files and LocalAppData state but Windows application-control enforcement blocked restart of the pre-existing unsigned executable. The workstation required emergency source-level recovery. That run remained `BLOCK` and is not lifecycle PASS evidence.

Canonical incident evidence:

`docs/evidence/APL_REL_014_OWNER_HOST_INCIDENT_2026-08-20.md`

APL-REL-014 may now run only in a disposable/isolated Windows VM or dedicated clean acceptance host where test failure cannot break the operator's normal network path.

Historical migration entry point:

`tools/windows_signed_set_lifecycle_acceptance_migration.ps1`

is now fail-closed by default. It requires the explicit `-IsolatedAcceptanceEnvironment` switch and delegates to the canonical lifecycle script; its former owner-host mutation/restart behavior is disabled.

Do not disable Smart App Control, App Control for Business or comparable Windows protections as a workaround.

## Acceptance input

Use the exact retained release directory copied into/provided to the isolated Windows acceptance environment:

`C:\Arvectum\Releases\0.2.3-russian-production`

The lifecycle script performs these checks in order:

1. verifies the external `PUBLISH` decision and exact release identity;
2. verifies the exact signed release set with the bundled Russian verifier;
3. verifies the sealed portable and installer hashes;
4. refuses to run over an already registered installer installation;
5. temporarily isolates any existing unmanaged/portable install directory, application state, and owned Run values;
6. installs the exact signed-set installer and runs `--status` smoke;
7. runs the same exact installer again and requires `REPAIR` maintenance mode;
8. deliberately damages the installed executable and stale maintenance state, then recovers through the cached repair installer;
9. requires the cached repair installer hash to equal the signed production installer hash;
10. uninstalls and verifies owned cleanup plus user-configuration and foreign-autostart preservation;
11. re-verifies the signed release set and artifact hashes after the lifecycle;
12. restores pre-existing test-environment state and emits external lifecycle evidence.

The script never writes into the signed release directory. Evidence is written beside it by default:

`C:\Arvectum\Releases\0.2.3-russian-production.lifecycle-acceptance.json`

The gate is complete only when the final console result is:

`APL-REL-014 Windows signed-set lifecycle acceptance: PASS`

and the evidence contains:

- `result = PASS`
- `environment_restored = true`
- fresh install PASS
- status smoke PASS
- same-version repair PASS
- corruption recovery PASS
- uninstall PASS
- user configuration preservation PASS
- foreign autostart preservation PASS
- post-lifecycle signed-set verification PASS

## Trust boundary

APL-REL-014 proves lifecycle behavior and detached Russian release-set integrity. It does **not** prove Microsoft Authenticode, SmartScreen or Smart App Control execution trust.

That separate production distribution boundary is tracked as `APL-WIN-014` in `docs/WINDOWS_APP_CONTROL_COMPATIBILITY.md`.
