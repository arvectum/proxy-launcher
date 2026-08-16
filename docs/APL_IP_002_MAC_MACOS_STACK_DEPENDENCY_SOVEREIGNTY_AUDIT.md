# APL-IP-002-MAC — macOS stack & dependency sovereignty audit

Status: **CONDITIONAL PASS** for source/CI/product architecture. APL-MAC-008 real-host acceptance remains mandatory before Gate R9.

## Inventory

| Component | Class | Provider/origin | Bundled | External network at runtime | Criticality / sovereignty note |
|---|---|---|---|---|---|
| frozen Python/Tk application | runtime | Python/PyInstaller ecosystem | yes | no | foreign build/runtime ecosystem; exact build versions locked |
| `/usr/sbin/networksetup` | host runtime | Apple/macOS | no | no | critical system-proxy control plane; cannot be replaced without changing platform architecture |
| LaunchAgents / plist format | host runtime interface | Apple/macOS | no | no | autostart only; per-user and non-privileged |
| `/usr/bin/hdiutil` | build/package | Apple/macOS | no | no | DMG build-only tool |
| `codesign` inspection | CI evidence | Apple/macOS | no | no | inspection only; no production identity is assumed |
| GitHub macOS 15 arm64/x64 runners | CI/build | GitHub + Apple-hosted image ecosystem | no | no end-user dependency | external build service; replaceable by Arvectum-controlled Mac builders |
| Apple production signing/notarization services | optional future release | Apple | no | yes when used | not required by current Russian-first roadmap; keep separate from functional runtime acceptance |

## Runtime autonomy

Normal proxy operation has no mandatory Arvectum cloud, Apple web API or third-party SaaS dependency. The product talks to local Apple system tooling and writes rollback/autostart state under the user's profile. The macOS platform itself is proprietary and foreign-controlled; therefore the task cannot claim full sovereign substitution of the operating-system control plane.

## Build sovereignty

The current CI path depends on GitHub-hosted macOS runners and PyPI acquisition of the frozen Python build set. The build scripts themselves are portable to an Arvectum-controlled physical Mac runner and do not require GitHub-specific APIs. A sovereign/restricted build perimeter can therefore mirror the pinned Python packages and run the same scripts locally.

## Findings

- **MAC-SOV-01 — P1:** macOS/Apple system tooling is intrinsically foreign platform infrastructure. This is accepted as a platform constraint, not hidden as an Arvectum-owned dependency.
- **MAC-SOV-02 — P1 build:** GitHub/PyPI are current build channels; controlled mirrors + self-hosted Mac runner are the replacement path.
- **MAC-SOV-03 — P2 optional distribution:** Apple production code signing/notarization can introduce online Apple-service dependency. It stays outside the Russian-first functional release gate unless distribution policy later requires it.
- **MAC-SOV-04 — PASS runtime autonomy:** no mandatory vendor SaaS is needed for ordinary proxy operation after installation.

## Acceptance

- [x] runtime/build/package/autostart dependencies classified;
- [x] bundled vs host-owned components separated;
- [x] external runtime/build network dependencies identified;
- [x] self-hosted build replacement path recorded;
- [x] optional Apple signing/notarization kept outside functional correctness claims;
- [ ] self-hosted/mirrored macOS production build perimeter — infrastructure debt;
- [ ] real macOS acceptance — APL-MAC-008.
