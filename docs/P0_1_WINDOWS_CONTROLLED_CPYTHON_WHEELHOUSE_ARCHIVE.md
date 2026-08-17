# [Win] P0.1 — controlled CPython + wheelhouse archive

Status: **DONE / P0.1 CLOSED 2026-08-17**

P0.1 closes the Windows build-input archival boundary. Repository-side acquisition, pinning and offline/hash-locked build controls are backed by a self-contained archive, an Arvectum-controlled primary copy, a physically separate removable offline copy and final Windows round-trip verification.

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

`prepare_windows_cpython_base.ps1` downloads the governed CPython installer and its official `.sigstore` bundle, but identity verification is explicitly executed with `sigstore verify identity --offline`. This prevents a live TUF refresh from becoming a recovery availability dependency while retaining signature, certificate identity/OIDC issuer and bundled transparency evidence checks. The manifest records `verification_mode=offline-bundle` and the trust-root source used by sigstore-python.

### Traditional installer collision boundary

The python.org Windows full installer is a registered product installer, not a portable extractor. A developer/acquisition laptop with an equivalent registered Python installation is therefore not required to install the archived interpreter during P0.1. `tools/install_verified_windows_cpython.ps1` remains the canonical clean/disposable-host recovery-install control for P0.2.

### Acquisition interpreter vs governed target interpreter

The Python executable that runs `pip download` is only an acquisition transport. `tools/prepare_windows_wheelhouse.ps1` explicitly targets:

- `--platform win_amd64`;
- `--python-version 3.12.10`;
- `--implementation cp`;
- `--abi cp312`;
- `--only-binary=:all:`;
- `--no-deps`;
- `--require-hashes`.

A newer trusted CPython can therefore perform acquisition, while the controlled product build itself still uses verified CPython `3.12.10` x64.

## Repository-side tooling

### `tools/archive_windows_build_inputs.ps1`

Network-free packager that re-checks CPython/wheelhouse manifests and hashes, copies only governed files, embeds governance locks, emits `controlled-archive-manifest.json`, and produces one ZIP plus SHA-256 sidecar and preparation evidence JSON.

Canonical archive name:

```text
arvectum-windows-build-inputs-cpython-3.12.10-x64.zip
```

### `tools/verify_windows_build_input_archive.ps1`

Network-free verifier that:

- verifies the ZIP against its SHA-256 sidecar before extraction;
- rejects missing/unexpected payload files;
- verifies every payload byte against `controlled-archive-manifest.json`;
- re-verifies nested CPython and wheelhouse manifests;
- requires exactly eight governed wheels;
- validates archived governance locks;
- with `-RequireCurrentRepositoryLocks`, requires archived locks to byte-match the current checkout.

## Governed archive identity

```text
archive = arvectum-windows-build-inputs-cpython-3.12.10-x64.zip
archive_bytes = 30996168
archive_sha256 = 4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886
cpython_version = 3.12.10
cpython_architecture = x64
cpython_installer = python-3.12.10-amd64.exe
cpython_installer_sha256 = 67b5635e80ea51072b87941312d00ec8927c4db9ba18938f7ad2d27b328b95fb
cpython_sigstore_verification = PASS
cpython_verification_mode = offline-bundle
wheelhouse_platform = win_amd64
wheelhouse_implementation = cp
wheelhouse_abi = cp312
wheel_count = 8
wheelhouse_hash_lock_sha256 = 6587ee8cc6e7528f3d86dcfcca16fb731b48102a7a24fc6f0f12363f79020943
```

## Controlled primary storage — PASS

Canonical Arvectum-controlled primary directory:

```text
/Users/Shared/Arvectum/ControlledArtifacts/ProxyLauncher/windows-build-inputs/sha256-4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886/
```

The exact ZIP, sidecar and preparation evidence JSON were transferred over authenticated private-LAN SCP, byte-matched the Windows source, and the three source files were then made read-only and `uchg`. The primary directory is not world-writable. Access and retention policies are recorded in `docs/P0_1_CONTROLLED_STORAGE_PROFILE.md`.

## Independent removable offline copy — PASS

Governed device label:

```text
ARVECTUM-1
```

Device characteristics at creation:

```text
filesystem = exFAT
capacity = 16.0 GB
external_removable = YES
```

Canonical macOS path used during creation:

```text
/Volumes/ARVECTUM-1/ProxyLauncher/windows-build-inputs/sha256-4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886/
```

The ZIP, sidecar and evidence byte-matched the primary copy, SHA-256 was verified from the removable device, `sync` passed, macOS software eject passed, and the device was physically disconnected from the primary host.

## Final Windows round-trip verification — PASS

Verification repository commit:

```text
1429e55959e9a3940b1f2e03e84f18fa7b05de0c
```

The exact offline bytes on `ARVECTUM-1` and a fresh retrieval of the Mac mini primary copy were both verified on Windows with package-index access disabled and:

```powershell
.\tools\verify_windows_build_input_archive.ps1 `
  -ArchivePath <exact-controlled-zip> `
  -RequireCurrentRepositoryLocks
```

Both returned:

```text
P0.1 CONTROLLED ARCHIVE VERIFICATION: PASS
```

Both ZIPs reported `30996168` bytes and SHA-256 `4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886`. ZIP, sidecar and evidence files byte-matched between retrieved primary and offline copies.

After the verifier, the operator safely ejected `ARVECTUM-1` from Windows, physically disconnected it and returned it to separate offline storage.

## P0.1 acceptance — CLOSED

All acceptance requirements are evidenced:

- exact CPython `3.12.10` x64 installer identity and Sigstore offline-bundle verification: **PASS**;
- exact eight-wheel CPython `3.12.10` / `win_amd64` / `cp312` wheelhouse: **PASS**;
- self-contained ZIP offline verifier: **PASS**;
- controlled primary archive byte identity: **PASS**;
- primary access/retention/sealing controls: **PASS**;
- separate removable offline copy: **PASS**;
- final Windows canonical verifier against offline bytes: **PASS**;
- final Windows canonical verifier against retrieved primary bytes: **PASS**;
- primary/offline ZIP, sidecar and evidence byte-match: **PASS**;
- final safe eject, physical disconnect and separate storage: **PASS**;
- secrets in final evidence: **NO**.

```text
P0.1 CLOSED: YES
```

Canonical completion evidence:

```text
docs/evidence/P0_1_COMPLETION_EVIDENCE.json
```

## Next action

**[Win] P0.2 — independent endpoint-denied sovereign recovery build.** Use only the controlled P0.1 archive as the CPython/wheelhouse source, deny public package endpoints during install/build, produce portable + installer + release evidence/SBOM, and compare resulting release evidence with the canonical candidate.
