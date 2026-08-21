# APL-IP-003 Slice 4 — routing policy ownership extraction evidence

Status: **MERGED / ENGINEERING SLICE COMPLETE**

Date: 2026-08-21

## Canonical merge

- Pull request: `#124` — `APL-IP-003 Slice 4 — routing policy ownership extraction`
- Merge commit: `0a4256d0f16bb0c798f96f9d4a618564f38b92c5`
- Pre-slice main baseline: `2a58c9d8c20e517bb1c98d90ae26afb4e5e117c7`
- Reviewed PR head: `420b9a13341e222c197c78a36b93ff0983701020`
- Product version: unchanged (`0.2.3`)

## Extracted ownership

`routing_policy.py` is now the canonical platform-neutral implementation owner, through the established mutable `proxy_core` compatibility seam, for:

- the built-in `DEFAULT_NO_PROXY` bypass policy;
- `no_proxy.txt` loading;
- normalized, de-duplicated and atomic `no_proxy.txt` persistence;
- raw URL / host / host:port / IPv6 / wildcard input normalization via `clean_domain`;
- destination-host normalization;
- boundary-safe domain, wildcard and loopback bypass evaluation via `host_bypasses_proxy`;
- PAC generation from the effective built-in and user exclusion sources.

The extraction intentionally does **not** take ownership of platform-specific system-proxy mutation. Windows/macOS/Linux backend/runtime responsibility remains outside `routing_policy.py`. Existing `routing_rules.py` and `routing_ownership.py` responsibilities are also unchanged.

## Regression contract preserved

The sealed Windows `0.2.3` routing behaviour remains the reference contract. The Slice 4 extraction preserves:

- the exact built-in bypass entries;
- comment/blank-line handling for `no_proxy.txt`;
- lowercase URL/host normalization and numeric host-port stripping;
- bracketed and raw IPv6 handling;
- wildcard matching semantics;
- boundary-safe exact/subdomain matching (`evilexample.com` does not match `example.com`);
- dynamic user exclusion reads without restart;
- the historical `_atomic_write_text` monkeypatch/persistence seam;
- PAC direct-list ordering/de-duplication and current local HTTP port selection;
- mutable `proxy_core` collaborator resolution required by the Windows compatibility adapter and existing regression tests.

No intentional routing, proxy-enforcement, backend-selection, configuration, release-version, or packaging behaviour change was introduced.

## Targeted Slice 4 coverage

`tests/test_routing_policy.py` adds direct coverage for:

- canonical implementation ownership;
- `no_proxy.txt` read semantics;
- atomic normalized persistence and de-duplication;
- URL, host:port, IPv6 and wildcard normalization;
- boundary-safe bypass evaluation;
- built-in localhost / IPv6 loopback bypass;
- dynamic `load_no_proxy` monkeypatch resolution through the compatibility seam;
- PAC generation and local HTTP port selection.

`tests/test_canonical_source_refactor.py` was extended so the canonical-source contract explicitly requires `routing_policy.py` and verifies the Slice 4 owner functions.

## GitHub Actions evidence

All 18 PR workflow runs completed with conclusion `success` for reviewed head `420b9a13341e222c197c78a36b93ff0983701020` before merge.

| Gate | Run | Result |
|---|---:|---|
| APL-IP-003 canonical source | `32482597380` | SUCCESS |
| Phase 5 Config and Security | `32482597216` | SUCCESS |
| Windows P0 portable | `32482597337` | SUCCESS |
| Windows installer | `32482597352` | SUCCESS |
| APL-IP-002-WIN controlled offline build | `32482597305` | SUCCESS |
| macOS packaging | `32482597393` | SUCCESS |
| APL-LNX-008 AppImage | `32482597276` | SUCCESS |
| APL-LNX-007 Debian package | `32482597367` | SUCCESS |
| Core backend contract | `32482597271` | SUCCESS |
| APL-DIAG-004 Doctor | `32482597257` | SUCCESS |
| APL-DIAG-003/006 Windows diagnostics + privacy | `32482597288` | SUCCESS |
| APL-DIAG-001/002 structured logging + secret redaction | `32482597448` | SUCCESS |
| SAST | `32482597308` | SUCCESS |
| Secret scan | `32482597323` | SUCCESS |
| Dependency vulnerability scan | `32482597392` | SUCCESS |
| SBOM | `32482597481` | SUCCESS |
| APL-IP-001 provenance | `32482597401` | SUCCESS |
| APL-LNX-006 Linux diagnostics support bundle | `32482597334` | SUCCESS |

### macOS runner note

The first ARM64 macOS packaging attempt completed all 40 macOS tests and the PyInstaller `.app` build successfully, then exited during DMG creation after the application build had completed. The Intel matrix job was successful. The failed ARM64 job was re-run without any source change and completed successfully, including DMG build/inspection and artifact upload. This is recorded as a transient packaging-runner / `hdiutil` flake rather than a Slice 4 code defect.

## Governance conclusion

Slice 4 is complete as an engineering refactor. It does **not** by itself declare the post-refactor source clean-IP approved and does not authorize a new clean-IP tag. The standing APL-IP-001 human/legal rights-basis gate remains required for final APL-IP-003 closure.
