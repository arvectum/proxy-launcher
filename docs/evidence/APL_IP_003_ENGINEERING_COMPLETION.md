# APL-IP-003 — engineering completion & post-refactor candidate

Status: **ENGINEERING REFACTOR COMPLETE — POST-REFACTOR CANDIDATE SELECTED; HUMAN/LEGAL CLEAN-IP APPROVAL PENDING**

Date: 2026-08-22

## Exact candidate

The protected-`main` post-refactor IP review candidate is:

- **`8ad54018e6d6251c906a06d09fd464c8931c14b2`**

This is the merge commit of PR `#163` (`APL-IP-003 Slice 23 — engineering completion contract`).

Final PR head:

- `1625e44ad1d3d96a5f7218545c74ffb1d85de93f`

GitHub compare from the final PR head to the protected-main candidate reports one merge-topology commit and **zero changed files**. Therefore the candidate file tree is byte-for-byte identical to the fully validated PR tree; the merge changed history topology, not candidate content.

## Final engineering audit verdict

No additional engineering refactor blocker was found after Slice 22.

The accumulated permanent guards prove:

- `proxy_core_legacy.py` is physically absent;
- all historical `core.<stdlib>` facade aliases tracked by the refactor are absent and have no live consumers;
- the composition root owns no live runtime implementation callable;
- maintained canonical sources describe current ownership rather than refactor history;
- current-tree repository identity is `arvectum/proxy-launcher`, with historical evidence explicitly bounded;
- regression method names no longer encode refactor slice numbers;
- GUI entry points do not import concrete platform backends directly;
- `backend_runtime` remains the concrete backend-selection owner;
- stale internal Windows backend vocabulary retired in Slice 22 has no live Python consumer;
- human historical Git identities are normalized through `.mailmap` without history rewrite;
- AI/bot/automation identities are not remapped to a human author;
- the sealed product version remains exactly `0.2.3`.

Slice 23 added `tests/test_engineering_completion_contract.py` and wired it into the Windows/macOS/Ubuntu canonical-source matrix so these completion conditions remain machine-enforced after the refactor.

## Final candidate CI evidence

Final PR head `1625e44ad1d3d96a5f7218545c74ffb1d85de93f` completed **8/8 triggered workflows successfully**:

- APL-IP-003 canonical source — Windows/macOS/Ubuntu: **SUCCESS**;
- APL-IP-001 provenance: **SUCCESS**;
- CycloneDX SBOM: **SUCCESS**;
- SAST: **SUCCESS**;
- dependency vulnerability scan: **SUCCESS**;
- secret scan: **SUCCESS**;
- Windows P0 portable: **SUCCESS**;
- Windows installer: **SUCCESS**.

Because the protected-main candidate has the identical file tree, these exact-head checks validate the candidate content.

### Windows final baseline proof

Windows clean-build evidence on the final Slice 23 tree records:

- **640 tests, OK**;
- product version: **0.2.3**;
- PyInstaller 6.22.0 standalone build: **SUCCESS**;
- PE/product metadata verification: **SUCCESS**;
- Documents canonical execution smoke: **SUCCESS**;
- packaged Doctor smoke: **SUCCESS**.

Windows installer evidence on the same tree records:

- pinned Inno Setup 6.7.1: **SUCCESS**;
- portable baseline / final EXE metadata: **SUCCESS**;
- synthetic predecessor lifecycle fixture: **SUCCESS**;
- canonical installer compile / metadata verification: **SUCCESS**;
- fresh / upgrade / repair / uninstall E2E: **SUCCESS**;
- Gate R6 acceptance matrix: **SUCCESS**.

### Cross-platform runtime/package proof carried by the unchanged runtime tree

Slice 23 changed only the completion test and canonical-source workflow; it changed no production runtime source. The immediately preceding Slice 22 final implementation tree completed **20/20 workflows successfully**, including:

- canonical-source Windows/macOS/Ubuntu;
- Core backend contract;
- macOS Apple Silicon and Intel `.app`/DMG build and inspection;
- Debian package;
- AppImage;
- Debian/Ubuntu acceptance;
- Linux diagnostics;
- Windows controlled offline build with Sigstore-verified CPython, exact wheelhouse, offline portable build and no-index-fallback proof;
- Windows portable and installer lifecycle/Gate R6;
- Phase 5 configuration/security, diagnostics, provenance, SAST, dependency, SBOM and secret gates.

No production file changed between that full platform matrix and the Slice 23 candidate.

## Regenerated provenance evidence

APL-IP-001 provenance run `32552042186` on the final Slice 23 head completed successfully and uploaded:

- artifact: `apl-ip-001-source-provenance`;
- artifact ID: `9470327809`;
- artifact digest: `sha256:36c9a9e267d38b1241d1e8afd17096bd7ce072c9665f56a38584054555c752bd`;
- recorded head SHA: `1625e44ad1d3d96a5f7218545c74ffb1d85de93f`.

The provenance manifest remains explicitly review-oriented: automated evidence does not claim copyright authorship or legal sign-off and requires human review/legal sign-off.

## Regenerated SBOM evidence

SBOM run `32552042326` on the final Slice 23 head completed successfully and uploaded:

- artifact ID: `9470330386`;
- artifact digest: `sha256:8e24e7cb03ee22380672eaf9b6b6333485cadf099471378745c8503956c405af`;
- recorded head SHA: `1625e44ad1d3d96a5f7218545c74ffb1d85de93f`;
- CycloneDX build-dependency SBOM validated against `requirements-build.lock.txt`.

The SBOM remains correctly bounded as a build-dependency SBOM; it is not misrepresented as the entire cross-platform shipped-payload inventory. Platform payload/license evidence remains governed separately by the package contracts and `THIRD_PARTY_NOTICES.txt`.

## Provenance / public-similarity boundary

Automated post-refactor work is complete for source inventory/hashes, provenance-marker surfacing, dependency/SBOM evidence, platform-package/license boundaries and engineering regression evidence.

A general public-code similarity search cannot honestly establish legal authorship or non-infringement by automation alone. The repository's existing IP provenance policy therefore continues to require a bounded human significant-source/public-similarity review of this exact candidate, investigation of any provenance findings, and reconciliation with the executed author-to-ООО rights basis.

This remaining work is a **human/legal approval gate**, not unresolved engineering refactor debt.

## APL-IP-003 status boundary

Engineering work under APL-IP-003 is complete through Slices 1–23.

The overall APL-IP-003 clean-IP lifecycle must **not** be marked legally `DONE`/`APPROVED` and no clean-IP tag may be created until an authorized human reviewer completes the post-refactor review and explicitly approves the exact candidate.

Remaining external gate:

1. review exact candidate `8ad54018e6d6251c906a06d09fd464c8931c14b2` and its provenance/SBOM/package evidence;
2. repeat bounded significant-source/public-similarity review;
3. reconcile the author-to-ООО exclusive-rights basis and applicable third-party obligations;
4. record explicit human/legal `APPROVED` only if no blocker remains;
5. only after that approval, create the governed clean-IP baseline/tag.

There is **no next engineering refactor slice** unless that human/legal review discovers a concrete technical remediation item.
