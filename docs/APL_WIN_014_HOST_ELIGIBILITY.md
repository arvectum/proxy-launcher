# APL-WIN-014 host eligibility

## Purpose

APL-WIN-014 is the real Windows App Control for Business execution-compatibility gate for Arvectum Proxy Launcher. It must not be converted into destructive experimentation on the normal owner workstation.

## Current owner-host decision — 2026-08-20

The current Windows owner workstation is **diagnostics-only and INELIGIBLE for the final APL-WIN-014 enforcement gate**.

Observed local facts from the owner-host preflight/policy diagnostic:

- Windows 11 Home, x64, build 26200;
- Smart App Control registry state `VerifiedAndReputablePolicyState=1` (`ENFORCE`);
- normal OpenCode/PowerShell token was not elevated; non-elevated `CiTool -lp -json` returned access denied;
- no new Code Integrity 3077 events were observed for the active network stack;
- 17 historical Arvectum 3077 events were found, none classified as the sealed production 0.2.3 binary;
- the currently present/running Arvectum executable is unsigned and does not match the sealed production 0.2.3 application hash;
- the live host network stack includes AmneziaVPN, NGate and Arvectum proxy components;
- current connectivity remained operational during read-only diagnostics.

These findings are **not** APL-WIN-014 PASS evidence. They are a safety decision that prevents mutation of the current owner host.

## Mandatory final-gate host requirements

The final APL-WIN-014 App Control for Business gate must run only on a **dedicated physical Windows acceptance host** that:

1. is not the normal owner workstation and does not carry valuable production/user network state;
2. runs a Windows edition appropriate for organization-managed App Control for Business acceptance (normally Windows 11 Pro, Enterprise, or Education), not Windows 11 Home;
3. permits elevated administrative policy inventory/management through the approved Windows App Control path;
4. has no dependency on the owner workstation's active proxy/VPN stack;
5. can be restored by normal host backup/recovery procedures without relying on the abandoned local VM path;
6. can execute the exact sealed release lifecycle while App Control remains enforced;
7. retains real Code Integrity evidence for Setup, first launch, GUI/core/PAC, rollback, repair, cross-version upgrade and uninstall.

## Owner-host prohibitions

On the current owner workstation, APL-WIN-014 must not:

- disable or reconfigure Smart App Control;
- modify `VerifiedAndReputablePolicyState`;
- deploy/remove/replace `.cip` policies;
- change ownership or ACLs of Smart App Control policy files;
- install/uninstall/replace the live Arvectum copy for acceptance purposes;
- stop or replace AmneziaVPN, NGate, proxy_core or other active network components;
- run destructive lifecycle acceptance;
- attempt to manufacture a final App Control for Business PASS from Smart App Control consumer evidence.

Read-only diagnostics remain allowed.

## Product boundary

Smart App Control and App Control for Business use the same Windows application-control foundation, but they are not interchangeable acceptance contours. Public unmanaged Smart App Control admission remains a separate distribution problem from enterprise App Control for Business compatibility through customer-managed base/supplemental policy or Managed Installer trust.

The Russian-first detached CryptoPro/Rutoken release signature proves governed release provenance/integrity; it does not by itself provide Windows embedded execution trust.

## Gate state

`APL-WIN-014 = HARNESS READY / OWNER HOST SAFETY DIAGNOSTIC COMPLETE / FINAL PHYSICAL ACB HOST PENDING`

Do not mark APL-WIN-014 PASS until evidence from an eligible dedicated physical App Control for Business host exists.
