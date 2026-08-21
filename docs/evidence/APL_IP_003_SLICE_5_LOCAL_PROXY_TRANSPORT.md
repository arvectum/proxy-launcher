# APL-IP-003 Slice 5 — local proxy transport ownership extraction evidence

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Canonical merge

- Pull request: `#126` — `APL-IP-003 Slice 5 — local proxy transport ownership extraction`
- Merge commit: `e2733e19172bff0c1c15df070fb6e1951bc50c2c`
- Pre-slice main baseline: `8385f73111345bd2b57af2af4aaf7b89b22a1271`
- Reviewed PR head: `e51b8ecb106ee7f6e143c6211eb374745f270c38`
- Product version: unchanged (`0.2.3`)

## Extracted ownership

`local_proxy_transport.py` is now the canonical platform-neutral local enforcement/transport implementation owner, through the established mutable `proxy_core` compatibility seam, for:

- `ProxyCore` construction and upstream preparation;
- upstream Basic authentication-token construction and failover iteration;
- HTTP proxy handling;
- HTTP CONNECT tunnelling;
- SOCKS5 destination parsing and tunnelling;
- PAC HTTP endpoint serving;
- bidirectional socket relay;
- listener creation, loopback binding and accept loops;
- proxy listener start/stop lifecycle;
- the SOCKS5 reply `BND.ADDR` protocol constant.

The extraction intentionally does **not** take ownership of process/PID status, CLI orchestration, system-proxy mutation, recovery, configuration persistence, or routing policy. The transport consumes the Slice 4 canonical `routing_policy.py` seams dynamically rather than implementing its own exclusion logic.

## Regression contract preserved

The sealed Windows `0.2.3` transport behaviour remains the reference contract. Slice 5 preserves:

- loopback-only HTTP/SOCKS/PAC listener binding;
- the established HTTP, SOCKS and PAC default/configured ports;
- upstream host filtering and invalid-port fallback to `8000`;
- Basic proxy-auth token construction from runtime username/password values;
- ordered upstream failover;
- direct HTTP routing for canonical `no_proxy` matches;
- direct CONNECT tunnelling for canonical `no_proxy` matches;
- direct SOCKS5 tunnelling for canonical `no_proxy` matches;
- upstream HTTP request authentication-header injection;
- upstream CONNECT request construction;
- SOCKS5 success/failure reply wire values;
- PAC path matching, content type, no-cache response and dynamic PAC generation;
- relay timeout/closure behaviour;
- listener lifecycle and `Already running` / port-bind failure semantics;
- dynamic compatibility seams for `socket`, `_normalize_host`, `host_bypasses_proxy`, `build_pac`, logging and settings.

No intentional transport, routing, backend-selection, system-proxy, process-ownership, CLI, release-version, or packaging behaviour change was introduced.

## Targeted Slice 5 coverage

`tests/test_local_proxy_transport.py` adds direct coverage for:

- canonical `ProxyCore` ownership;
- SOCKS5 reply protocol constant parity;
- upstream credential/token preparation and invalid-port fallback;
- dynamic routing-policy resolution by the HTTP handler;
- dynamic `build_pac` resolution through the compatibility seam;
- PAC 200/404 serving behaviour.

`tests/test_canonical_source_refactor.py` was extended so the canonical-source contract explicitly requires `local_proxy_transport.py` and verifies that all `ProxyCore` transport methods are owned by that module.

The pre-existing `tests/test_proxy_core.py` transport scenarios were intentionally left in place and exercised the newly installed class without being rewritten. They cover direct HTTP, direct CONNECT, direct SOCKS5, upstream-auth routing and live PAC listener/health-check behaviour.

## GitHub Actions evidence

All 18 PR workflow runs completed with conclusion `success` for reviewed head `e51b8ecb106ee7f6e143c6211eb374745f270c38` before merge.

| Gate | Run | Result |
|---|---:|---|
| APL-IP-003 canonical source | `32483901091` | SUCCESS |
| Phase 5 Config and Security | `32483901096` | SUCCESS |
| Windows P0 portable | `32483901003` | SUCCESS |
| Windows installer | `32483901121` | SUCCESS |
| APL-IP-002-WIN controlled offline build | `32483901156` | SUCCESS |
| macOS packaging | `32483901068` | SUCCESS |
| APL-LNX-008 AppImage | `32483901023` | SUCCESS |
| APL-LNX-007 Debian package | `32483901072` | SUCCESS |
| Core backend contract | `32483901094` | SUCCESS |
| APL-DIAG-004 Doctor | `32483901061` | SUCCESS |
| APL-DIAG-003/006 Windows diagnostics + privacy | `32483901143` | SUCCESS |
| APL-DIAG-001/002 structured logging + secret redaction | `32483901049` | SUCCESS |
| SAST | `32483901108` | SUCCESS |
| Secret scan | `32483901038` | SUCCESS |
| Dependency vulnerability scan | `32483901030` | SUCCESS |
| SBOM | `32483901101` | SUCCESS |
| APL-IP-001 provenance | `32483900990` | SUCCESS |
| APL-LNX-006 Linux diagnostics support bundle | `32483901047` | SUCCESS |

### Independent full-suite evidence

The `Phase 5 Config and Security` workflow executed the full unit suite on both Ubuntu and Windows after the extraction. Both matrix jobs completed successfully. This is important because the historical `tests/test_proxy_core.py` transport tests import `proxy_core.ProxyCore` through the public compatibility boundary and therefore exercised the new canonical class rather than a purpose-built Slice 5 test double.

The controlled offline build also completed successfully through verified CPython acquisition, exact Windows wheelhouse acquisition, offline archive verification, canonical portable build and the explicit no-package-index-fallback proof.

## Governance conclusion

Slice 5 is complete as an engineering refactor. It does **not** by itself declare the post-refactor source clean-IP approved and does not authorize a new clean-IP tag. The standing APL-IP-001 human/legal rights-basis gate remains required for final APL-IP-003 closure.
