# Gate R2 — Final Windows Release Gate

**Status:** PASS
**Date:** 2026-08-15

## Repository
* Canonical repository: `arvectum/proxy-launcher`
* Canonical branch: `main`
* Release: `v0.2.3`
* Release tag SHA: `cf8da51e91f86c8142a4eb0590d8e249a49e4ce5`

## Controlled Release Verification
* Controlled release of `v0.2.3` published successfully
* Published assets:
  * `Arvectum-Proxy-Launcher-0.2.3-windows-x64-portable.zip`
  * `Arvectum-Proxy-Launcher-0.2.3-windows-x64-setup.exe`
  * `SHA256SUMS.txt`
* SHA-256 portable: `8968007331dfe85b920914c1cdaf77634fed5814d23858ba952df43c60ed6294`
* SHA-256 installer: `e50b88934616c84ca218d8f70b0b9337024721ee4289c17d4b750d09db79db6b`

## Original Tag Workflow
Original `v0.2.3` tag workflow successfully passed:
* Release context validation
* Windows portable build
* Portable execution smoke
* Windows installer build
* Fresh install smoke
* Status smoke
* Upgrade smoke
* Uninstall smoke

## Controlled Recovery Process
* Original release workflow failed exclusively on publish-stage due to incorrect artifact handoff in reusable workflow
* Controlled recovery used **exact artifacts from original tag-run**
* Byte-for-byte SHA-256 of published assets matches tag-run artifacts
* Tag `v0.2.3` **was not moved or recreated**

## Post-Release State
* PR #15 / `APL-REL-007.1` was merged after controlled release, fixing only CI artifact handoff
* Current post-release `main` differs from release SHA only by CI workflow/regression test changes
* **No change to product/runtime payload**
* Post-release CI for current `main` is green:
  * Windows P0 portable
  * Windows installer
  * Dependency vulnerability scan
  * Secret scan
  * SBOM
  * SAST
  * Release Evidence Package
  * GitVerse mirror

## Scope Statement
**Gate R2 confirms successful completion and integrity of final Windows controlled release v0.2.3 and closes Windows release gate for the current unsigned distribution track.**

**Gate R2 does NOT confirm Windows Authenticode code signing, publisher reputation, or Microsoft SmartScreen reputation. These tasks belong to separate Windows distribution trust/signing track and are NOT grounds for FAIL of current Gate R2.**

## Integrity Verification Summary
* ✅ Tag `v0.2.3` unchanged at SHA `cf8da51e91f86c8142a4eb0590d8e249a49e4ce5`
* ✅ Published asset SHA-256 matches tag-run artifacts
* ✅ Original release workflow succeeded through smoke tests
* ✅ Controlled recovery used original artifacts
* ✅ Post-release CI improvements do not affect product payload
* ✅ All mandatory release verification gates satisfied

---
*Gate R2 audit complete. Windows release gate closed for v0.2.3.*