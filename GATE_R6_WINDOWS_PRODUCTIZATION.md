# Gate R6 — Windows Productization

## Gate status

**STATUS: PASS**

Accepted implementation evidence:

- PR: `#47` — `APL-WIN-010..013 — Windows productization and Gate R6`;
- accepted implementation commit: `5538fe10dbb356fb771f13e6106c7840f401d87e`;
- Windows installer workflow run: `31950894227` (`Windows installer`, run #168) — **SUCCESS**;
- the same candidate commit also completed `Windows P0 portable`, `APL-DIAG-004 Doctor`, `SAST`, `Secret scan`, `Dependency vulnerability scan`, and `SBOM` with **SUCCESS**.

The accepted Windows installer run completed the canonical portable build and final EXE metadata check, synthetic predecessor build, canonical Setup build and metadata check, full Windows RC lifecycle E2E, machine RC acceptance matrix, and evidence upload without a failed mandatory step.

## Scope

Gate R6 closes the Windows productization layer after recovery/config-security hardening. It covers:

- APL-WIN-010 — final executable metadata and Windows branding;
- APL-WIN-011 — RC packaging and machine-enforced acceptance matrix;
- APL-WIN-012 — fresh install / upgrade / repair / uninstall E2E;
- APL-WIN-013 — final Windows install/support documentation.

It consumes the already completed Windows safety foundations including rollback/recovery, DPAPI configuration security, safe autostart, single-instance behavior, repair/uninstall ownership boundaries and diagnostics/supportability.

## Mandatory evidence

All mandatory Gate R6 evidence is PASS for the accepted implementation commit:

1. canonical Windows clean build PASS;
2. canonical Inno Setup build PASS;
3. application PE metadata PASS;
4. installer PE metadata PASS;
5. fresh install + `--status` smoke PASS;
6. clean fresh uninstall PASS;
7. predecessor-to-current upgrade PASS;
8. damaged-binary repair PASS;
9. final uninstall PASS;
10. persistent configuration preserved across upgrade/repair/uninstall;
11. foreign startup state preserved;
12. canonical portable/setup filenames and package contents PASS;
13. final SHA-256 evidence generated;
14. final user-facing install/portable docs present with no internal engineering milestone labels;
15. `out/windows-rc-e2e.json` result PASS;
16. `out/windows-rc-acceptance.json` result PASS and zero failures.

## Release artifact boundary

Only these Windows product artifacts are eligible for product release:

- `Arvectum-Proxy-Launcher-X.Y.Z-windows-x64-portable.zip`;
- `Arvectum-Proxy-Launcher-X.Y.Z-windows-x64-setup.exe`.

The synthetic predecessor setup exists only to exercise the installer upgrade state machine in CI. It is prohibited from RC acceptance and release publication.

## Signing boundary

Gate R6 is a **Windows productization gate, not a false code-signing attestation**.

The Russia-first signing architecture remains governed by APL-REL-009 and APL-REL-010. Production embedded code signing is not considered activated merely because Gate R6 passes. Until the real approved signing path is activated, release/support documentation must continue to state the actual unsigned/signing status and rely on canonical hashes/release provenance for byte integrity.

This signing boundary does not invalidate the productization checks above; it prevents Gate R6 from claiming cryptographic publisher trust that has not yet been proven.

## Closure

Gate R6 was closed only after exact-commit CI evidence was green. The subsequent closure commit changes this evidence record only and must itself retain the same CI invariants before merge to `main`.
