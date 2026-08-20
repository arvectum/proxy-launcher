# APL-WIN-014 — real App Control for Business local gate

Status: **HARNESS READY / REAL WINDOWS 11 EVIDENCE REQUIRED**

This gate closes only on a disposable/isolated Windows 11 VM or dedicated acceptance host with **App Control for Business actually enforced**. CI, mocks, Smart App Control screenshots, or a successful run after disabling protection are not acceptance evidence.

## Safety boundary

- Never disable Smart App Control, App Control for Business, Defender, or another Windows protection to make Arvectum run.
- Never change `VerifiedAndReputablePolicyState`.
- The Arvectum release/installer does not deploy App Control policies.
- App Control policy deployment remains an explicit lab/customer-IT action.
- `ReferenceFullHash` is required for the current 0.2.3 exact-hash acceptance because Setup alone does not cover generated maintenance/uninstall binaries.
- Final PASS requires a **real cross-version upgrade from a distinct sealed previous build**. Same-version repair is not upgrade evidence.

## Canonical scripts

1. `tools/windows_app_control_local_gate.ps1`
   - `Prepare`: exact release verification + reference installation + `ReferenceFullHash` trust pack; policy deployment is not performed.
   - `Enforced`: current 0.2.3 Setup, first GUI launch, core, PAC, Windows system proxy, rollback, canonical repair/corruption/uninstall lifecycle, Code Integrity evidence.
2. `tools/windows_app_control_upgrade_acceptance.ps1`
   - installs a distinct sealed baseline under its own active supplemental trust;
   - upgrades in place to exact 0.2.3;
   - proves exact post-upgrade bytes and state preservation;
   - uninstalls and checks Code Integrity enforcement evidence.
3. `tools/windows_app_control_local_gate_complete.ps1`
   - the **only final completion entry point**;
   - emits final PASS only if both the real upgrade gate and the exact 0.2.3 enforced gate PASS.

## Phase A — prepare current 0.2.3 trust pack

Run from elevated PowerShell on the isolated acceptance VM while the organization/lab base policy is present in an appropriate staging/audit state:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\windows_app_control_local_gate.ps1 `
  -Phase Prepare `
  -BasePolicyId '{BASE-POLICY-GUID}' `
  -ReleaseDirectory 'C:\Arvectum\Releases\0.2.3-russian-production' `
  -TrustPackDirectory 'C:\Arvectum\Evidence\APL-WIN-014\trust-pack' `
  -EvidenceDirectory 'C:\Arvectum\Evidence\APL-WIN-014' `
  -IsolatedAcceptanceEnvironment
```

Expected result: `PREPARED`, not `PASS`. The generated trust pack must be `ReferenceFullHash` and target the supplied base-policy ID.

## Phase B — policy deployment outside Arvectum tooling

Using the isolated lab/customer App Control management path:

1. confirm the base policy permits supplemental policies;
2. if the base policy is signed, authorize the supplemental signer as required by that policy model;
3. deploy the generated current-release supplemental `.cip`;
4. deploy/activate a separate exact trust path for the sealed baseline build used by the upgrade test;
5. put the base policy into the intended **Enforced** state;
6. reboot if required by the policy-management path;
7. verify both supplemental policies are visible with `CiTool -lp -json`.

Arvectum scripts intentionally do not perform these policy mutations.

## Baseline required for the real upgrade proof

The operator/OpenCode must provide a distinct previous sealed Windows installer and its governed evidence:

- baseline version, e.g. `0.2.2` if that exact package is available;
- exact baseline Setup SHA-256;
- exact installed baseline `Arvectum Proxy Launcher.exe` SHA-256;
- active supplemental policy ID that trusts those baseline bytes and is bound to the same base policy.

If a trustworthy previous package cannot be recovered, **do not manufacture one and do not substitute 0.2.3 repair**. The upgrade portion remains BLOCK until a distinct governed baseline exists (or until a separately governed Managed Installer upgrade acceptance is implemented).

## Phase C — canonical final acceptance

After both baseline and current supplemental trust are active and the base policy is enforced:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\windows_app_control_local_gate_complete.ps1 `
  -BasePolicyId '{BASE-POLICY-GUID}' `
  -BaselineSupplementalPolicyId '{BASELINE-SUPPLEMENTAL-GUID}' `
  -BaselineSetupPath 'C:\Arvectum\Releases\baseline\ArvectumProxyLauncher-Setup.exe' `
  -BaselineSetupSha256 '<64-hex-sha256>' `
  -BaselineApplicationSha256 '<64-hex-sha256>' `
  -BaselineVersion '0.2.2' `
  -ReleaseDirectory 'C:\Arvectum\Releases\0.2.3-russian-production' `
  -TrustPackDirectory 'C:\Arvectum\Evidence\APL-WIN-014\trust-pack' `
  -EvidenceDirectory 'C:\Arvectum\Evidence\APL-WIN-014' `
  -IsolatedAcceptanceEnvironment
```

## Required final evidence

`C:\Arvectum\Evidence\APL-WIN-014\apl-win-014-final-result.json` must contain `result = PASS` and reference two subordinate PASS records:

- `apl-win-014-upgrade-result.json`;
- `apl-win-014-enforced-result.json`.

The subordinate evidence must prove, at minimum:

- requested base policy remained enforced;
- current and baseline supplemental trust were active/on-disk where required;
- exact 0.2.3 Setup executed under enforcement;
- first GUI process creation succeeded;
- proxy core ran;
- PAC served `FindProxyForURL` from `127.0.0.1:8082`;
- Windows `AutoConfigURL` used the governed local PAC endpoint;
- explicit rollback restored the network state;
- repair/corruption recovery/uninstall lifecycle passed;
- real distinct-version upgrade passed and preserved per-user state;
- exact post-upgrade 0.2.3 application and cached repair hashes matched the sealed release;
- no Arvectum Code Integrity event 3077 was recorded during the tested operations;
- App Control remained enforced after acceptance.

Only then may the roadmap local gate be changed from `PENDING` to `PASS`.
