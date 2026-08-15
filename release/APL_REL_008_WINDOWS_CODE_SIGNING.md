# APL-REL-008 — Windows code signing / Authenticode foundation

**Status:** FOUNDATION READY / PRODUCTION SIGNING NOT ACTIVE  
**Date:** 2026-08-15

## Goal

Establish a safe, testable Windows Authenticode layer without changing the already released unsigned `v0.2.3` artifacts and without placing exportable private-key material in the repository.

## Implemented foundation

- `tools/windows_authenticode.ps1`
  - signs PE files with a certificate already available through the Windows certificate store;
  - selects the certificate by thumbprint;
  - requires Code Signing EKU (`1.3.6.1.5.5.7.3.3`);
  - uses SHA-256 file digest;
  - requires RFC 3161 timestamping with SHA-256 for production signing;
  - verifies with SignTool Authenticode policy (`/pa /all`);
  - optionally enforces the exact expected publisher subject;
  - does not accept a PFX file or private-key password.
- `.github/workflows/windows-authenticode.yml`
  - runs static contract tests;
  - performs a Windows smoke against the real PyInstaller-built PE;
  - creates a one-day self-signed Code Signing certificate only inside the disposable GitHub runner;
  - proves that an unsigned PE is rejected;
  - signs and verifies a copy of the real application executable;
  - removes the ephemeral test certificate after the job.
- `tests/test_windows_authenticode_foundation.py`
  - protects SHA-256/RFC 3161 requirements;
  - protects the no-PFX/no-password repository contract;
  - protects the activation boundary between foundation and production signing.

## Production configuration contract

The generic certificate-store provider uses these non-secret configuration values:

- `WINDOWS_SIGNING_CERT_THUMBPRINT` — thumbprint of the production code-signing certificate exposed in `CurrentUser\\My` (or `LocalMachine\\My` when explicitly selected).
- `WINDOWS_SIGNING_TIMESTAMP_URL` — CA/provider RFC 3161 timestamp endpoint.
- `WINDOWS_SIGNING_EXPECTED_PUBLISHER` — exact certificate subject expected in final signed binaries.
- `SIGNTOOL_PATH` — optional explicit path to `signtool.exe`; otherwise the script locates SignTool from PATH or the installed Windows SDK.

The private key is deliberately outside this contract. It must remain in the hardware token/HSM/managed signing service or another non-exportable provider supported by the selected certificate vendor.

## Activation boundary

APL-REL-008 does **not** silently switch current public releases to signed mode. Production activation requires a separately verified signing identity/provider and must then change the release pipeline so that:

1. the **portable EXE** is signed before the portable ZIP and its internal checksum are created;
2. the signed portable EXE is used as the installer payload;
3. the **installer EXE** is signed after Inno Setup compilation;
4. both final signatures are verified against the expected publisher before smoke testing/publication;
5. SHA256 manifests are generated only after all signing operations are complete;
6. release publication fails closed if either required signature is missing or invalid.

Until that activation is completed, the canonical public release track remains the already documented unsigned track.

## Security rules

- Never commit `.pfx`, `.p12`, token PINs, private keys, or signing passwords.
- Never log secret provider credentials or hardware-token PINs in GitHub Actions.
- Do not use SHA-1 as the release signing digest.
- Production signatures must be timestamped; `-SkipTimestamp` is reserved for disposable self-signed CI smoke only.
- A signed artifact is a different byte sequence from the unsigned artifact; checksums must always be calculated after signing.
- Existing release tags and assets remain immutable. `v0.2.3` is not re-signed in place.

## Acceptance criteria for foundation

- [x] Provider-neutral SignTool wrapper exists.
- [x] SHA-256 signing contract exists.
- [x] RFC 3161 SHA-256 timestamp is mandatory in production mode.
- [x] Authenticode verification fails closed.
- [x] Expected publisher can be enforced.
- [x] Repository contract contains no PFX/password path.
- [x] Windows CI smoke signs a real application PE with an ephemeral test certificate.
- [x] Current unsigned release pipeline is not silently mutated.
- [ ] Production certificate/provider is acquired and validated.
- [ ] Production release pipeline signs portable EXE and installer EXE.
- [ ] First signed release passes SmartScreen/reputation observation and release gate.
