# APL-CLIENT-002 — Confirmed customer baseline freeze

Status: FROZEN / CUSTOMER PASS
Freeze date: 2026-08-14
Platform: Windows x64
Canonical product version: 0.2.3
Historical customer track: portable P0 hotfix

## Authoritative identity

The authoritative identity of this frozen baseline is the immutable source commit and the
cryptographic SHA-256 digests of the delivered binary artifacts:

```text
Source commit:
4d2ab937ce3c775ca627fa2deeefe3fb464ef48d

Portable ZIP SHA256:
683362A03785FD31625F5C570DC661B3562CE23C822FBDB07A8E27365BDA7909

EXE SHA256:
CD802FA0E7C48653098ADBEAF9B654CD6138196D8B2BB8DA2979198962803868
```

> Commit SHA and binary SHA-256 values are authoritative. Branch names, filenames and temporary CI artifact IDs are convenience locators only.

## Source snapshot

```text
Repository:
arvectum/proxy-launcher

Build-time branch:
release/windows-rc2.1-final

Exact source commit:
4d2ab937ce3c775ca627fa2deeefe3fb464ef48d

Commit message:
test(windows): normalize canonical path assertions

Relevant preceding hotfix:
cc2f1b90843cc3bb3a518f1214271f5e9b2dbee1

Hotfix message:
fix(windows): keep P0 portable usable under App Control
```

> Reconstruct the source from the immutable commit SHA, not from a moving branch head.

## CI evidence

Historical GitHub Actions evidence for the frozen baseline:

```text
Workflow:
Windows P0 portable

Run ID:
31745739554

Job ID:
94599728020

Head SHA:
4d2ab937ce3c775ca627fa2deeefe3fb464ef48d

Conclusion:
SUCCESS

Python:
3.12.10

PyInstaller:
6.22.0

Automated tests:
89 tests
OK
3 skipped

Windows Documents execution smoke:
PASS

Artifact ID:
9198914448

Actions wrapper ZIP SHA256:
B73F353694E1793430D8411EFC826090851416AA912D04FEE5DEB9BCD95DDB98

Inner portable ZIP SHA256:
683362A03785FD31625F5C570DC661B3562CE23C822FBDB07A8E27365BDA7909

EXE SHA256:
CD802FA0E7C48653098ADBEAF9B654CD6138196D8B2BB8DA2979198962803868
```

The 3 skipped tests belonged to the installer track, which is absent from the portable P0
branch, so they are expected skips.

## Customer-facing traceability

Historical customer-facing filename:

```text
Arvectum-Proxy-Launcher-Windows-0.2.3-P0-portable.zip
```

Notes:

* `P0` is an internal/customer engineering milestone, not part of the canonical product version.
* The canonical version of this baseline is `0.2.3`.
* The historical filename is not canonical public release naming.
* The file with that name is not committed to the repository; it exists only for traceability.

## Frozen behaviour/changelog

The following behaviour is frozen as part of this confirmed customer baseline:

* portable execution remains usable when Windows blocks handoff to the permanent Documents copy;
* autostart is prohibited/disabled when canonical execution is not confirmed;
* Run entries are not redirected to an unconfirmed/blocked executable;
* persistent state is stored in `%LOCALAPPDATA%\Arvectum\ProxyLauncher`;
* canonical EXE handoff goes to `%USERPROFILE%\Documents\ArvectumProxyLauncher` when Windows allows it;
* App Control diagnostic helpers are included;
* a read-only native QA helper is included;
* canonical path regression assertions are normalized;
* routing, DPAPI credential storage, rollback/recovery and process ownership protections are part of the baseline.

```text
Customer validation: PASS — portable version confirmed working.
```

## Tag policy decision

```text
No public Git tag is created for APL-CLIENT-002.
```

Rationale:

* `P0`, `RC`, `final` are engineering milestones;
* engineering milestones must not appear in public canonical tags;
* creating `v0.2.3` solely for this customer freeze would incorrectly turn a baseline marker into a canonical public release;
* the immutable source SHA plus the ZIP SHA and EXE SHA fully identify this baseline.

## Freeze gate

- [x] Customer validation PASS
- [x] Exact source commit identified
- [x] Source snapshot immutable
- [x] Exact CI run identified
- [x] Windows automated QA PASS
- [x] Portable ZIP SHA256 recorded
- [x] EXE SHA256 recorded
- [x] Customer-facing filename recorded
- [x] Changelog recorded
- [x] Public-tag policy respected

APL-CLIENT-002 RESULT: PASS — CONFIRMED CUSTOMER BASELINE FROZEN.