# APL-REC-005 — Network change tests

## Status

Implemented.

## Purpose

Arvectum Proxy Launcher must survive ordinary Windows network changes without corrupting proxy recovery state or requiring the proxy core to be restarted. Typical changes include Wi-Fi roaming, Ethernet disconnect/reconnect, VPN/interface changes, DHCP renewal, DNS changes, and short periods without upstream connectivity.

APL-REC-005 captures those expectations as regression tests around the existing architecture.

## Invariants

1. HTTP, SOCKS5, and PAC listeners bind only to `127.0.0.1`, never to a physical adapter address. An adapter address change therefore does not invalidate the local proxy endpoints.
2. PAC health checks always address the loopback PAC endpoint and do not depend on the currently selected NIC.
3. An already captured WinINET rollback snapshot is immutable across later network changes. The launcher must never replace the original pre-activation state with a transient post-change state.
4. Exact Arvectum PAC ownership is determined from `AutoConfigURL`; unrelated changes to manual proxy, autodetect, or override values do not silently transfer or revoke ownership.
5. Upstream proxy hostnames are retained as hostnames rather than pre-resolved at core construction time, allowing later socket connects to follow DNS changes.
6. A failed direct connection caused by a transient adapter outage does not poison the running core. The next request performs a fresh connection attempt and can succeed without restart.
7. A failed upstream connection caused by a transient network outage likewise does not poison the core. The next request creates a fresh upstream socket and can recover without process restart.

## Safety boundary

Network changes are treated as transport events, not as permission to rewrite or recapture recovery evidence.

`network change -> keep original rollback evidence -> keep loopback listeners -> reconnect per request`

If Windows or another application replaces the PAC with a foreign value, the ownership rules introduced by APL-REC-002/APL-REC-004 still apply: the foreign state is not writable merely because a network transition occurred.

## Automated coverage

Coverage is implemented in `tests/test_network_change.py`. The suite is platform-independent and uses mocked socket/registry boundaries, so CI never changes the host network configuration.

## Relationship to previous recovery tasks

- APL-REC-001 defines the recovery lifecycle.
- APL-REC-002 defines ownership/evidence authority.
- APL-REC-003 proves crash recovery behavior.
- APL-REC-004 proves foreign proxy state is preserved.
- APL-REC-005 proves ordinary network/interface changes do not invalidate listeners, overwrite original rollback evidence, or permanently poison connectivity.
