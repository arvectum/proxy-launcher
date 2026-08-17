# Arvectum Proxy Launcher — remaining local / human / infrastructure backlog

Updated: 2026-08-17

This file contains only work that cannot be truthfully completed by hosted repository automation alone. The protected Windows `0.2.3` system-proxy baseline must remain unchanged while these items are executed.

## P0 — Windows sovereign-build infrastructure closure

**Why first:** release recoverability and dependency sovereignty are higher risk than adding new features.

### P0.1 Archive controlled build inputs

Status: **AUTONOMOUS PREPARATION COMPLETE / LOCAL-INFRA ACCEPTANCE PENDING**.

Repository-side preparation is complete:

- `tools/archive_windows_build_inputs.ps1` re-verifies the governed CPython/wheelhouse bytes and produces one self-contained ZIP, SHA-256 sidecar and preparation evidence record without network access;
- `tools/verify_windows_build_input_archive.ps1` independently verifies the archive offline, including nested manifests, exact wheel count and governance locks;
- `docs/P0_1_WINDOWS_CONTROLLED_CPYTHON_WHEELHOUSE_ARCHIVE.md` is the canonical operator runbook and acceptance contract.

Required local/infrastructure boundary:

- choose an Arvectum/Russian-controlled artifact perimeter reachable during release recovery;
- acquire and verify the exact CPython 3.12.10 x64 bootstrap used by the canonical build;
- acquire the exact verified Windows wheelhouse defined by `requirements-build.windows-x64.hashes.txt` plus `wheelhouse-manifest.json`;
- build and offline-verify the P0.1 self-contained archive;
- store the archive, SHA-256 sidecar and evidence record in the controlled perimeter;
- record immutable SHA-256 values, retrieval path, access/retention policy and an offline copy location.

Acceptance:

- the controlled copy byte-matches the pinned/verified inputs and the locally prepared archive SHA-256;
- the archive passes `tools/verify_windows_build_input_archive.ps1` without network access;
- a fresh build host can acquire all bootstrap/build inputs from the controlled perimeter without PyPI or python.org;
- the evidence record identifies the storage source, offline-copy location and hashes without exposing secrets.

### P0.2 Independent endpoint-denied recovery build

Required local/infrastructure boundary:

- Windows x64 build host outside the normal GitHub hosted-runner dependency path (self-hosted runner or equivalent controlled machine);
- public package endpoints denied during the actual install/build phase;
- inputs supplied only from the controlled CPython/wheelhouse perimeter.

Acceptance:

- canonical portable/installer build succeeds in offline/hash-locked mode;
- release evidence and SBOM are produced;
- hashes/diffs are compared against the canonical candidate and any expected nondeterminism is documented;
- GitVerse/self-hosted recovery procedure is proven rather than merely documented.

## P1 — APL-LNX-010 real Astra Linux acceptance + Gate R8

Required local boundary: a real supported Astra Linux graphical host/session.

Start with the repository collector:

```bash
bash qa/collect_astra_acceptance_preflight.sh
```

Then execute the APL-LNX-010 acceptance matrix on the actual `.deb` candidate, including:

- install/start/GUI;
- runtime/backend detection;
- NetworkManager capability/preflight;
- enable/sync/disable and exact rollback;
- autostart/session behavior;
- crash/restart/reboot recovery;
- uninstall/update and user-state preservation;
- diagnostics/support bundle privacy review.

Gate R8 closes only if real-host evidence passes. Hosted Ubuntu CI is not a substitute.

## P2 — APL-IP-001 authorized human/legal sign-off

Required human/legal boundary: authorized reviewer(s) able to judge authorship, licensing and chain of title for ООО «Арвектум».

Use:

- `docs/APL_IP_001_PROVENANCE_HARDENING.md`;
- `docs/APL_IP_001_HUMAN_LEGAL_SIGNOFF.md`;
- final source provenance manifest;
- final SBOM(s) and third-party notices;
- actual employee/contractor/pre-company/brand-asset rights documents.

Acceptance:

- significant-source review complete;
- all final shipped artifacts reconciled with SBOM/licenses/notices;
- chain-of-title evidence verified;
- decision in the sign-off record is **APPROVED**;
- only then create a clean IP tag pointing to the exact reviewed commit (recommended convention: `ip-clean/<product-version>/<YYYY-MM-DD>`).

Automation must not mark this complete on behalf of a human reviewer.

## P3 — APL-ROUTE-003 Windows per-application routing product decision

Required product/external-platform boundary before further native implementation.

Production WFP connect-redirection requires a kernel/native enforcement path whose normal Windows production loading/signing chain creates an external Microsoft/accepted-EV dependency. Choose one path deliberately:

1. accept that dependency for an optional per-app Windows SKU;
2. adopt a separately reviewed already-signed third-party enforcement component;
3. prove a supported user-mode architecture with equivalent semantics;
4. defer Windows per-app routing and keep the proven system-proxy/domain/IP product as the production line.

Do **not** use test-signing/developer mode as a production workaround.

If path 1 or 2 is chosen, the next local work becomes native install/update/remove ownership, signing, privileged WFP enforcement, loop prevention, crash/reboot rollback and real Windows acceptance.

## P4 — APL-MAC-008 real macOS acceptance + Gate R9

Required local boundary: a real Mac with a normal interactive user session.

Start with:

```bash
bash qa/collect_macos_acceptance_preflight.sh
```

Then execute the real acceptance matrix, including:

- `.app`/DMG launch and GUI;
- `networksetup` capability/preflight;
- enable/sync/disable and exact rollback;
- LaunchAgent/autostart ownership;
- crash/restart/reboot recovery;
- update/remove behavior and user-state preservation;
- diagnostics/support bundle privacy review.

Gate R9 closes only from real-host evidence.

Apple production signing/notarization remains a later distribution-policy task under the current Russian-first strategy, not a functional correctness gate.

## P5 — controlled Linux/macOS build-input mirrors

Required infrastructure boundary: Russian/Arvectum-controlled artifact/mirror storage and the corresponding build-host routing/credentials.

Scope after P0:

- archive/mirror pinned Python/build inputs required by Linux and macOS packaging;
- archive the exact AppImage build/runtime inputs used by the release process;
- add immutable hashes and recovery instructions;
- run at least one build with public package endpoints unavailable.

This is medium priority because Windows is the customer-proven primary platform and should receive sovereignty closure first.

## Deferred feature work after the gates above

- Astra per-application routing prototype: only after the Windows routing policy is settled and a real Astra privileged test host is available; expected direction is controlled cgroup/socket identity plus nftables/policy-routing.
- macOS per-application routing: only after entitlement/distribution-model proof for NetworkExtension/managed per-app routing.
- international Apple/Microsoft signing/notarization paths: remain lower priority than the Russian-first production/release path unless product strategy changes.

## Completion discipline

Do not relabel any item above as complete from mocks, hosted CI, documentation, or synthetic evidence. Close each item only from the named real-host, infrastructure, external-platform, or human/legal evidence boundary.
