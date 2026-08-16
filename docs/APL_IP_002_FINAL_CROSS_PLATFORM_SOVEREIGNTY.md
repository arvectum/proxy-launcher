# APL-IP-002-FINAL — cross-platform stack & dependency sovereignty verdict

Status: **COMPLETE — CONDITIONAL PASS**. This consolidates APL-IP-002-WIN, APL-IP-002-LNX and APL-IP-002-MAC; it does not waive their open remediation/local-acceptance items.

## Cross-platform verdict

| Dimension | Windows | Linux/Astra | macOS |
|---|---|---|---|
| End-user runtime autonomy | GREEN | GREEN | GREEN |
| Mandatory vendor SaaS at runtime | none | none | none |
| OS/platform lock-in | Windows accepted exception | Linux distro + NetworkManager prerequisite | Apple/macOS accepted platform dependency |
| Build input reproducibility | RED/AMBER | AMBER | AMBER |
| Release packaging | portable + Inno Setup | `.deb` + AppImage | `.app` + DMG |
| Privilege model | Windows native | NetworkManager/PolicyKit, no custom helper | Apple `networksetup`, no custom helper |
| Current CI provider concentration | GitHub | GitHub | GitHub macOS runners |
| Real target-host gate | customer Windows baseline already proven separately | APL-LNX-010 | APL-MAC-008 |

## Shared findings

1. **SO-FINAL-001 — P0 Windows build inputs.** Windows still lacks a repository-enforced offline wheelhouse/hash-locked acquisition path and controlled CPython base artifact. Do not claim a sovereign Windows build until the APL-IP-002-WIN-R1..R5 drill succeeds.
2. **SO-FINAL-002 — P1 CI concentration.** All three platform lanes can currently use GitHub-hosted CI. The scripts are portable, but independent/self-hosted Russian recovery lanes are not yet proven.
3. **SO-FINAL-003 — P1 artifact/provenance controls.** Exact versions/digests exist in several places, but final-payload SBOM/notices/provenance reconciliation belongs to APL-IP-001.
4. **SO-FINAL-004 — platform exceptions.** Windows and macOS necessarily depend on foreign proprietary operating-system interfaces inside those SKUs. Astra/Linux is the preferred path when Russian-OS compatibility/sovereignty is a procurement requirement.
5. **SO-FINAL-005 — positive runtime property.** No supported desktop SKU requires an Arvectum cloud control plane, telemetry SaaS, license server or vendor API merely to switch/restore system proxy state.

## Release policy consequence

- **Russian controlled deployments:** prioritize Windows portable/installer with Russian signing path and the `.deb` Astra/Linux lane; AppImage remains an optional portability artifact with an extra upstream runtime stub.
- **macOS:** support as a separate platform SKU without representing Apple infrastructure as sovereign; Apple signing/notarization stays a distribution-policy decision rather than functional correctness prerequisite.
- **Build continuity:** retain GitHub for normal productivity but eliminate it and public package repositories as single points of release failure through controlled mirrors/self-hosted lanes.

## Final acceptance

- [x] Windows sovereignty audit exists and retains its P0/P1 remediation backlog.
- [x] Linux/Astra sovereignty audit covers runtime/build/package dependencies.
- [x] macOS sovereignty audit covers Apple/Python/build dependencies.
- [x] cross-platform exceptions and provider concentration are explicit.
- [x] no unsupported claim of full sovereignty is made.
- [ ] Windows offline/endpoint-denied sovereign-build drill.
- [ ] independent GitVerse/self-hosted build/recovery proof.
- [ ] APL-IP-001 final source/provenance/human-review sign-off.
