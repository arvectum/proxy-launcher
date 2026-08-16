# APL-REC-007 — Failure injection

This suite validates fail-closed recovery behavior by deliberately failing one
operation at each roadmap boundary.

## Injection matrix

| Failure point | Formal state when failure is observed | Required outcome |
| --- | --- | --- |
| Save original state | `SAVE_ORIGINAL` | Abort before mutation and return to verified-safe `OFF` |
| Apply proxy mutation | `APPLY` | Enter `RESTORE`; never claim `OFF` until restore and OFF verification succeed |
| Verify active state | `VERIFY(ACTIVE)` | Enter `RESTORE`; never commit `ACTIVE` |
| Start local listener | `VERIFY(ACTIVE)` | Treat listener startup as part of ACTIVE proof; enter `RESTORE` and never commit `ACTIVE` |
| Restore original state | `RESTORE` | Stay in `RESTORE`, remain recovery-required, retry restore, then verify `OFF` |

## Safety invariants

1. A failure before `APPLY` may return directly to `OFF` because no governed
   network mutation has started.
2. After `APPLY` begins, failures cannot skip `RESTORE`.
3. `ACTIVE` is never committed when active verification or listener startup
   fails.
4. A failed restore operation does not advance state or transition history.
5. `OFF` is reported only after a successful restore followed by explicit OFF
   verification.
6. Every injected failure scenario has a deterministic path to the same safe
   terminal `OFF` state once the failing external operation succeeds on retry.

## Automated coverage

`tests/test_failure_injection.py` injects deterministic failures at all five
boundaries and checks both the immediate fail-closed state and eventual safe
recovery. The matrix test additionally proves that no injected path terminates
in a false `ACTIVE` or false `OFF` state.

The suite is platform-independent: operating-system side effects are represented
as explicit operations around the formal recovery state machine, allowing the
failure contract to run on every CI platform without changing real proxy or
registry settings.
