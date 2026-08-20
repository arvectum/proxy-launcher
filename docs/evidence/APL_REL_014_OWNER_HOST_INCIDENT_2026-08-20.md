# APL-REL-014 owner-host incident — 2026-08-20

Status: **RECOVERED / OWNER-HOST ACCEPTANCE PROHIBITED**

## Scope

During migration-style APL-REL-014 execution on the owner's normal Windows workstation, the pre-existing registered `0.2.3` runtime was quiesced after a verified rescue snapshot had been created. The legacy executable was then blocked by Windows application-control enforcement when the wrapper attempted to restore the original runtime.

The failure occurred before canonical signed-set lifecycle phases completed. The generated lifecycle evidence therefore had `result=BLOCK` and an empty `phases` object; it must not be represented as APL-REL-014 PASS evidence.

## Observed facts retained as sanitized evidence

- Exact signed release preflight: PASS.
- Production release: `v0.2.3-ru.2`.
- Release-policy commit: `47823585c42da54ab51dc2246583dc24d74d4ba6`.
- Installer SHA-256: `5808bde9d0ac45048d50bc256878519257f53bf0a9fa523a81ccb2eff0e21414`.
- Portable ZIP SHA-256: `62d313547b4d8c2c8e6951d6cd866bb954fdf199ad7650063c8ed3bfbc455801`.
- Pre-existing local EXE was a non-sealed legacy `0.2.3` build and was not used as production release evidence.
- Legacy install-tree restoration: exact fingerprint PASS.
- Legacy LocalAppData state-tree restoration: exact fingerprint PASS.
- Original runtime restoration: BLOCK because Windows application-control policy refused execution of the restored legacy EXE.
- Independent rescue snapshot was preserved.

## Recovery

A source-level emergency recovery was executed using the existing controlled local Python 3.12 runtime and repository source tree:

1. current LocalAppData state, Internet Settings and Run registry values were backed up;
2. the canonical source `--rollback` path restored network settings successfully;
3. `proxy_settings.json` remained present and parseable;
4. the proxy core was started from source;
5. PAC listener `127.0.0.1:8082` became healthy;
6. the GUI was started from source;
7. Windows system proxy returned to the owned PAC URL;
8. Windows protection was not disabled;
9. the blocked legacy EXE and the original APL rescue directory were preserved.

Final emergency recovery result: **PASS**.

## Root cause / product implication

The Russian-first detached CryptoPro/Rutoken release signature proves release-set integrity but does not provide an embedded Windows Authenticode execution trust signal. Windows Smart App Control / application-control policy may therefore block an unsigned executable even when detached release evidence is valid.

This is a real distribution-compatibility boundary, not merely an acceptance-harness issue.

## Mandatory corrective controls

1. **Do not run destructive APL-REL-014 lifecycle acceptance on a normal owner workstation again.**
2. Real lifecycle acceptance must run in a disposable/isolated Windows VM or dedicated clean acceptance machine where loss of the test runtime cannot affect the operator's connectivity.
3. Owner-host migration wrappers are historical/forensic only and must not be used as the canonical acceptance path.
4. Keep Smart App Control / Windows application-control protections enabled; do not weaken host security to make the unsigned executable run.
5. Track Windows application-control compatibility as a separate production distribution blocker. A detached Russian signature alone must not be represented as satisfying Smart App Control execution trust.
6. Retain the owner-host recovery directories until the workstation has been normalized to a supported permanent distribution path.

## APL-REL-014 verdict

`BLOCK` on owner-host. No lifecycle PASS is claimed.

Next acceptable execution environment: isolated Windows acceptance VM/host only.
