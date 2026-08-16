# APL-WIN-007 — Production-safe autostart

Status: **implemented**

## Goal

Make Windows logon autostart safe for production use without requiring elevation and without allowing Arvectum Proxy Launcher to overwrite or delete autostart entries it cannot prove it owns.

## Canonical mechanism

The production mechanism is the current-user Windows Run value:

`HKCU\Software\Microsoft\Windows\CurrentVersion\Run\ArvectumProxyLauncher`

The value launches only the canonical managed Launcher executable with `--start`. Portable fallback sessions are never allowed to register themselves for logon startup.

A scheduled task named `ArvectumProxyLauncher` is treated only as a legacy compatibility mechanism. New releases do not create it.

## Safety contract

1. **Per-user only.** Autostart uses HKCU and does not request administrator rights.
2. **Canonical executable only.** A frozen build may register only the managed executable prepared by the existing canonical handoff/self-heal boundary.
3. **No foreign overwrite.** If the Run value exists but is not provably an Arvectum `--start` command, enable is refused and the value is left untouched.
4. **Fail closed on registry-read errors.** An unreadable Run value is not treated as “missing”; the launcher refuses to change autostart rather than risk overwriting unknown state.
5. **Write verification.** After enabling, the Run value is read back and must exactly match the intended command and pass the existing Arvectum ownership check.
6. **Legacy-task ownership is action-based.** A scheduled task is considered owned only when an `<Exec>` action itself resolves to a proven Arvectum start command. Merely mentioning an Arvectum path elsewhere in task XML is insufficient.
7. **No foreign task deletion.** A same-named legacy task that is not provably owned is never deleted or rewritten.
8. **Complete disable.** Disabling autostart removes both the owned Run value and any owned legacy scheduled task. Cleanup does not stop after deleting only one mechanism.
9. **Deletion verification.** Owned mechanisms are queried again after cleanup. A surviving owned entry is reported as an error and the checkbox is refreshed from real state.
10. **Migration is non-destructive.** Enabling writes and verifies the canonical Run value before deleting an owned legacy task. If a newly-created Run value would leave duplicate startup because legacy cleanup failed, that newly-created value is rolled back.

## UX

The existing checkbox remains the single user control. It reflects actual owned autostart state after every operation. Configuration is still required before enable, and portable fallback continues to disable the control with an actionable explanation.

## Verification

`tests/test_autostart_safety.py` covers:

- action-based scheduled-task ownership;
- rejection of deceptive task XML;
- post-write Run-value verification;
- rollback when legacy cleanup would leave a duplicate startup path;
- simultaneous cleanup of owned Run and legacy task;
- failure reporting when an owned task survives deletion;
- preservation of foreign same-named entries through the existing GUI ownership contract.

The implementation also passes the repository Bandit SAST gate; the only XML parse site is explicitly documented as parsing local `schtasks` output for a fixed task name rather than remote or user-supplied XML.

The full repository regression suite and Windows CI are required before merge.
