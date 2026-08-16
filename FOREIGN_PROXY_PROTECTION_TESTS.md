# APL-REC-004 — Foreign proxy protection tests

## Status

Implemented.

## Purpose

Recovery is allowed to modify only proxy state that can be proven to belong to Arvectum Proxy Launcher. A foreign PAC, manual proxy, recovery command, or ambiguous recovery artifact must never become writable merely because it resembles an Arvectum value.

APL-REC-004 turns that non-interference boundary into regression tests.

## Protected boundaries

The test suite proves the following rules:

1. PAC ownership is exact and structural. Query strings, fragments, credentials, another host, port, path, or scheme do not match the Arvectum PAC.
2. A foreign `ArvectumProxyLauncherRecovery` Run value is neither replaced nor deleted by recovery enablement.
3. Name/substring resemblance is insufficient ownership evidence. Commands outside known Arvectum locations remain foreign even when their filenames contain Arvectum-like text.
4. WinINET restore without a complete valid backup is a no-op. No registry values are written or deleted when rollback ownership cannot be proven.
5. A foreign PAC is never classified as an orphaned Arvectum PAC and therefore cannot enter destructive orphan cleanup.
6. Recovery disablement leaves a foreign Run value untouched.

## Safety invariant

`foreign or ambiguous state -> preserve state -> do not mutate -> do not claim recovery ownership`

The application may log a diagnostic or leave recovery pending, but it must prefer a visible/manual recovery condition over destroying a proxy configuration that could belong to another application, administrator, VPN, enterprise policy, or user.

## Coverage

Automated coverage lives in `tests/test_foreign_proxy_protection.py` and is platform-independent through mocked Windows registry boundaries. The tests run in the normal Python CI suite and do not mutate the host running CI.

## Relationship to previous recovery tasks

- APL-REC-001 defines legal recovery state transitions.
- APL-REC-002 defines ownership/evidence authority.
- APL-REC-003 injects crashes into the governed lifecycle.
- APL-REC-004 proves the recovery implementation fails closed around foreign proxy and recovery state.
