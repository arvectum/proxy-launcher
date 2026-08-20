# APL-WIN-014 — Windows application-control execution compatibility

Status: **ACTIVE / PRODUCTION DISTRIBUTION BLOCKER**

## Problem

Windows `0.2.3` is governed by the Russian-first release contour: the exact release manifest is signed and verified with the controlled CryptoPro/Rutoken identity. That detached signature proves release-set integrity and provenance but does not embed a Windows Authenticode signature into the executable.

A real owner workstation with Windows application-control enforcement refused to execute the restored legacy Arvectum Proxy Launcher EXE. The same host recovered successfully when the product was run from repository source under an already trusted local Python runtime.

This proves that release integrity and Windows execution trust are separate controls.

## Security rule

Do **not** disable Smart App Control, App Control for Business, Defender application-control policy, or comparable Windows protections as a product workaround.

Do **not** claim that the current detached Russian release signature provides SmartScreen/Smart App Control/Authenticode trust.

## Required outcome

Choose and prove at least one supported Windows distribution path that works on a representative application-control-enforced Windows host without weakening host security.

Candidate paths must be evaluated in this order:

1. Russian/domestic code-signing route that can produce a Windows-recognized embedded Authenticode signature on the final EXE/installer under the target deployment trust model.
2. Controlled enterprise deployment path where the customer's Windows application-control policy explicitly trusts Arvectum publisher/hash/catalog evidence without requiring public Microsoft ecosystem reputation.
3. A separately governed trusted launcher/runtime distribution architecture, only if it preserves product security, upgrade/recovery semantics and Russian sovereignty requirements.
4. International Microsoft-trusted public code-signing identity remains a lower-priority fallback and must not silently become the primary Russian-market dependency.

Source-mode execution through a trusted Python runtime is an emergency owner-host recovery mechanism only. It is not the Windows production distribution format.

## Acceptance requirements

APL-WIN-014 closes only when all of the following are demonstrated:

- exact final Windows executable/installer identity is known;
- execution succeeds on a representative Windows 11 host with application-control enforcement enabled;
- no user instruction requires disabling or bypassing Windows protection;
- install, first launch, core start, GUI launch, repair, upgrade and uninstall paths are covered;
- proxy rollback/recovery remains available if the application is prevented from starting after installation;
- the Russian detached release-evidence signature remains independently verifiable;
- documentation clearly distinguishes release provenance from Windows execution trust;
- CI/static contracts prevent future claims that detached signing alone satisfies Authenticode/Smart App Control.

## Relation to APL-REL-014

APL-REL-014 destructive lifecycle acceptance is prohibited on a normal owner workstation after the 2026-08-20 incident. It may run only in a disposable/isolated Windows acceptance environment.

The owner workstation remains in temporary source-recovery mode until a supported permanent Windows execution-trust path is chosen and accepted.

Canonical incident evidence: `docs/evidence/APL_REL_014_OWNER_HOST_INCIDENT_2026-08-20.md`.
