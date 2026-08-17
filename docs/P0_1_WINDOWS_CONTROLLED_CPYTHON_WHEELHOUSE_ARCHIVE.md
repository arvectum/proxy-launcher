# [Win] P0.1 — controlled CPython + wheelhouse archive

Status: **AUTONOMOUS PREPARATION COMPLETE / LOCAL-INFRA ACCEPTANCE PENDING**

P0.1 closes the remaining Windows build-input archival boundary. Repository-side acquisition, pinning and offline/hash-locked build controls already existed; this task adds the missing self-contained archive and offline verification layer needed before the bytes are moved into an Arvectum/Russian-controlled artifact perimeter.

## Governed inputs

The archive is built only from already verified repository-governed inputs:

- CPython `3.12.10` x64 from `BUILD_PYTHON_VERSION`;
- CPython identity lock `tools/python-windows-base.lock`;
- CPython acquisition output from `tools/prepare_windows_cpython_base.ps1`;
- exactly eight Windows build wheels from `requirements-build.windows-x64.hashes.txt`;
- wheelhouse acquisition output from `tools/prepare_windows_wheelhouse.ps1`;
- `requirements-build.lock.txt` and the Windows SHA-256 hash lock.

No application runtime dependency is added by P0.1.

### Sigstore network boundary

`prepare_windows_cpython_base.ps1` downloads the governed CPython installer and its official `.sigstore` bundle, but the identity verification itself is explicitly executed with `sigstore verify identity --offline`. For bundle verification, this prevents an unrelated TUF metadata refresh from becoming a release-recovery availability dependency while retaining the signature, certificate identity/OIDC issuer and bundled transparency evidence checks. The manifest records `verification_mode=offline-bundle` and the trust-root source used by sigstore-python.

As with any offline Sigstore verification, this trades live trust-root freshness for deterministic availability: the verifier uses the latest cached trust root or the root baked into the pinned sigstore-python version. Therefore the governed verifier version remains pinned, and future maintenance may separately archive a refreshed trust configuration if stronger revocation freshness is required for disconnected recovery.

## Repository-side tooling added

### `tools/archive_windows_build_inputs.ps1`

Network-free packager that:

1. re-checks the CPython acquisition manifest, installer size/SHA-256 and Sigstore-verification result;
2. re-checks `wheelhouse-manifest.json`, the committed hash-lock digest and all eight wheel sizes/SHA-256 values;
3. copies only governed files into a clean staging tree;
4. embeds the four governance locks required to identify the build-input set;
5. emits `controlled-archive-manifest.json` with every payload path, size and SHA-256;
6. creates one ZIP plus a SHA-256 sidecar and a local preparation evidence JSON.

Default archive name:

`arvectum-windows-build-inputs-cpython-3.12.10-x64.zip`

The local preparation evidence intentionally reports `ARCHIVE_PREPARED_NOT_YET_CONTROLLED_PERIMETER_PROVEN`; creating the ZIP on the build laptop alone does not close P0.1.

### `tools/verify_windows_build_input_archive.ps1`

Network-free verifier that:

- verifies the ZIP against its SHA-256 sidecar before extraction;
- rejects missing/unexpected payload files;
- verifies every payload byte against `controlled-archive-manifest.json`;
- re-verifies the nested CPython and wheelhouse manifests;
- requires exactly eight governed wheels;
- validates archived governance locks;
- with `-RequireCurrentRepositoryLocks`, requires the archived locks to byte-match the current checkout.

## Local acquisition and archive preparation

Run from a clean Windows x64 checkout of the exact P0.1 commit/PR after repository checks pass.

```powershell
$ErrorActionPreference = 'Stop'

# Existing trusted local Python is used only to acquire/verify the locked CPython bootstrap.
.\tools\prepare_windows_cpython_base.ps1 `
  -VerifierPython python.exe `
  -OutputDirectory .\artifact\windows-cpython-base

# Install the already verified CPython bootstrap into an isolated build path.
$ControlledPython = .\tools\install_verified_windows_cpython.ps1 `
  -VerifiedBaseDirectory .\artifact\windows-cpython-base `
  -TargetDirectory .\artifact\controlled-python

# Acquire the exact hash-locked Windows wheel set with that controlled CPython.
.\tools\prepare_windows_wheelhouse.ps1 `
  -PythonExecutable $ControlledPython `
  -OutputDirectory .\artifact\windows-wheelhouse

# Package already-verified bytes. This step itself performs no network access.
$Archive = .\tools\archive_windows_build_inputs.ps1 `
  -CpythonBaseDirectory .\artifact\windows-cpython-base `
  -WheelhouseDirectory .\artifact\windows-wheelhouse `
  -OutputDirectory .\artifact\p0-1

# Verify the prepared archive offline and require governance-lock byte equality.
.\tools\verify_windows_build_input_archive.ps1 `
  -ArchivePath $Archive `
  -RequireCurrentRepositoryLocks
```

## Controlled-perimeter transfer

The operator must copy all three files produced for the archive into the chosen Arvectum/Russian-controlled storage location:

- the ZIP;
- `<archive>.zip.sha256`;
- `<archive>.zip.evidence.json`.

The controlled storage copy must have an explicit retrieval path/identifier, access policy, retention policy and a second offline copy location. Secrets/credentials must not be placed in the evidence record.

After copying, run `tools/verify_windows_build_input_archive.ps1` directly against the controlled-storage copy (or against a fresh byte-for-byte retrieval from it), with public package endpoints unavailable during verification.

## P0.1 acceptance

P0.1 may be marked **DONE** only when all of the following are evidenced:

- CPython is exactly `3.12.10` x64 and its acquisition manifest records `sigstore-identity-pass`;
- CPython identity verification used the governed offline bundle mode and expected identity/OIDC issuer;
- the wheelhouse contains exactly the eight governed wheels and byte-matches the committed SHA-256 lock;
- the self-contained ZIP passes the offline verifier;
- the archive SHA-256 recorded at creation exactly matches the controlled-storage copy/retrieval;
- the archive and sidecar are stored inside the selected Arvectum/Russian-controlled perimeter;
- a separate offline copy location is recorded;
- storage retrieval path/identifier, retention policy and access policy are recorded without secrets;
- no PyPI/python.org access is required to verify or retrieve the controlled archived build inputs.

A GitHub Actions artifact, a local staging directory, documentation alone, or a successful hosted build does **not** close P0.1.

## Evidence to return

Return a concise report containing:

- exact repository commit SHA used;
- Windows edition/version and architecture;
- prepared archive filename, byte size and SHA-256;
- CPython installer filename and SHA-256 from `cpython-base-manifest.json`;
- CPython `verification_mode` and expected identity/OIDC issuer;
- wheel count and hash-lock SHA-256 from `wheelhouse-manifest.json`;
- offline verifier final PASS output;
- controlled storage type and non-secret retrieval path/identifier;
- offline-copy type/path identifier;
- access/retention policy summary;
- explicit statement whether P0.1 is fully closed.

## Next action after P0.1 PASS

**[Win] P0.2 — independent endpoint-denied sovereign recovery build.** Use only the controlled P0.1 archive as the CPython/wheelhouse source, deny public package endpoints during install/build, produce portable + installer + release evidence/SBOM, and compare the resulting release evidence with the canonical candidate.
