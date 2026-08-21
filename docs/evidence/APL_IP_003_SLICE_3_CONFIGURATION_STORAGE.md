# APL-IP-003 Slice 3 — configuration storage & recovery extraction evidence

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Canonical merge

- Pull request: `#122` — `APL-IP-003 Slice 3 — configuration storage & recovery extraction`
- Merge commit: `9a59d1dfe5687fb8fafa59811be8c2fff994c9b0`
- Pre-slice main baseline: `b54dc35cf0f2213a281367dd411a53f717887af9`
- Product version: unchanged (`0.2.3`)

## Extracted ownership

`configuration_storage.py` is now the canonical implementation owner, through the established mutable `proxy_core` compatibility seam, for:

- versioned settings schema/model validation;
- runtime/storage settings normalization;
- Windows DPAPI credential protection and decoding;
- atomic byte/JSON/text persistence;
- last-known-good settings snapshots;
- corruption quarantine and metadata evidence;
- deterministic last-known-good/default recovery;
- `load_settings` and `save_settings`.

Application/state path ownership remains in `application_filesystem.py` from Slice 2. `no_proxy` parsing and normalization remain in the historical compatibility layer for this bounded slice, while persistence continues to route through the extracted canonical atomic writer.

No routing or network-enforcement behaviour was intentionally changed.

## Regression contract preserved

The existing configuration/security contract remains authoritative and was exercised without weakening:

- unknown/future configuration fails closed;
- local proxy/PAC ports remain validated and distinct;
- Windows credentials-at-rest use DPAPI;
- legacy plaintext migration never creates a plaintext last-good copy;
- atomic replacement failure preserves the previous primary configuration;
- durable writer uses `fsync`;
- read-only diagnostic loads do not quarantine corrupted configuration;
- corrupted primary configuration is quarantined and last-known-good is restored when valid;
- corrupted primary/backup fall back deterministically to programmatic defaults with recovery evidence;
- locked/unavailable settings are treated as I/O failures, not corruption;
- `no_proxy` keeps the established atomic-writer monkeypatch seam.

## GitHub Actions evidence

All 18 PR workflow runs completed with conclusion `success` for head `48bbfec8fff0b8f9bc0a6d3c5b663da240e53703` before merge.

Key Slice 3 gates:

| Gate | Run | Result |
|---|---:|---|
| APL-IP-003 canonical source | `32481358591` | SUCCESS |
| Phase 5 Config and Security | `32481358558` | SUCCESS |
| Windows P0 portable | `32481358643` | SUCCESS |
| Windows installer | `32481358626` | SUCCESS |
| APL-IP-002-WIN controlled offline build | `32481358639` | SUCCESS |
| macOS packaging | `32481358675` | SUCCESS |
| APL-LNX-008 AppImage | `32481358699` | SUCCESS |
| APL-LNX-007 Debian package | `32481358668` | SUCCESS |
| Core backend contract | `32481358628` | SUCCESS |
| APL-DIAG-004 Doctor | `32481358605` | SUCCESS |
| APL-DIAG-003/006 Windows diagnostics + privacy | `32481358588` | SUCCESS |
| APL-DIAG-001/002 structured logging + secret redaction | `32481358716` | SUCCESS |
| SAST | `32481358590` | SUCCESS |
| Secret scan | `32481358663` | SUCCESS |
| Dependency vulnerability scan | `32481358638` | SUCCESS |
| SBOM | `32481358718` | SUCCESS |
| APL-IP-001 provenance | `32481358629` | SUCCESS |
| APL-LNX-006 Linux diagnostics support bundle | `32481358658` | SUCCESS |

## Governance conclusion

Slice 3 is complete as an engineering refactor. It does **not** by itself declare the post-refactor source clean-IP approved and does not authorize a new clean-IP tag. The standing APL-IP-001 human/legal rights-basis gate remains required for final APL-IP-003 closure.
