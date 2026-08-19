# [Win] P0.2-B — Inno Setup 6.7.1 sovereignty preparation

Status: **AUTONOMOUS PREPARATION PASS / CONTROLLED ACQUISITION PENDING / OFFLINE STAGING PENDING / ENDPOINT-DENIED INSTALLER RECOVERY PENDING**.

This sub-gate removes the repository-side ambiguity around the Windows installer compiler while preserving the real-host evidence boundary. It does **not** claim that Inno Setup has already been acquired, archived, staged into `ARVECTUM-P0-2-RECOVERY`, or used for an endpoint-denied build.

## Exact upstream identity

The accepted compiler input is frozen to:

- product: Inno Setup;
- exact version: `6.7.1`;
- immutable upstream release tag: `is-6_7_1`;
- upstream release commit short id: `cfdf489`;
- installer: `innosetup-6.7.1.exe`;
- expected bytes: `10,619,024`;
- expected SHA-256: `4d11e8050b6185e0d49bd9e8cc661a7a59f44959a621d31d11033124c4e8a7b0`;
- required Authenticode publisher: `Pyrsys B.V.`;
- detached Inno Setup signature: `innosetup-6.7.1.exe.issig`;
- release public key: `def02.ispublickey`;
- pinned public-key id: `def020edee3c4835fd54d85eff8b66d4d899b22a777353ca4a114b652e5e7a28`;
- license text is archived alongside the toolchain input.

Canonical lock: `tools/inno-setup-windows.lock`.

The release URL is version-specific. Recovery must never substitute `latest`, winget resolution, Chocolatey resolution, a web installer, or another Inno Setup version.

## Trust model

The controlled-input trust decision is split deliberately between connected acquisition and endpoint-denied recovery.

### Connected acquisition host

Run on a Windows host with public access only for the acquisition step:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\prepare_windows_inno_setup_base.ps1 `
  -OutputDirectory C:\P0_2_STAGE\inno-setup-6.7.1-base
```

The script:

1. reads the repository lock;
2. downloads the exact installer from the immutable GitHub release;
3. downloads the detached `.issig`, release public key and license;
4. rejects any installer whose size differs from `10,619,024` bytes;
5. rejects any installer whose SHA-256 differs from the pinned value;
6. requires Windows Authenticode status `Valid`;
7. requires the signer subject to contain `Pyrsys B.V.`;
8. verifies the pinned `def02` public-key id;
9. records hashes of all controlled bundle files in `inno-setup-base-manifest.json`;
10. does **not** execute the downloaded installer.

Optional defense in depth on an acquisition machine with GitHub CLI available:

```powershell
gh release verify-asset C:\P0_2_STAGE\inno-setup-6.7.1-base\innosetup-6.7.1.exe `
  --repo jrsoftware/issrc
```

This optional command is not a recovery dependency and is not required inside the endpoint-denied VM.

### Arvectum-controlled retention

After connected verification, preserve the complete directory as one controlled input set:

- `innosetup-6.7.1.exe`;
- `innosetup-6.7.1.exe.issig`;
- `def02.ispublickey`;
- `LICENSE.txt`;
- `inno-setup-base-manifest.json`.

At minimum, retain the verified set in Arvectum-controlled storage and a separate offline copy using the same byte-match/separation discipline already proven for P0.1. Do not treat a public URL, GitHub release availability, winget cache or an installed developer-workstation copy as controlled storage.

The controlled acquisition/retention sub-gate is **not complete** until real artifact hashes and storage evidence exist.

## Endpoint-denied VM installation

Only after the verified set has been staged into the disposable P0.2 guest while VirtualBox NIC remains `NONE`, install it into an explicit recovery-tool path. Example:

```powershell
powershell -ExecutionPolicy Bypass -File D:\P0_2_INPUTS\source\tools\install_verified_windows_inno_setup.ps1 `
  -VerifiedBaseDirectory D:\P0_2_INPUTS\controlled-inputs\inno-setup-6.7.1-base `
  -TargetDirectory C:\P0_2_TOOLS\Inno-Setup-6.7.1
```

The offline installer script:

- requires the acquisition manifest to record `locked-sha256+authenticode-pass`;
- re-hashes the installer and checks its recorded byte size;
- re-hashes the detached signature, public key and license against the manifest;
- performs no `Invoke-WebRequest` or `Invoke-RestMethod` call;
- invokes Inno Setup's documented `/PORTABLE=1` mode with `/CURRENTUSER` and an explicit `/DIR`, avoiding a normal uninstall/ARP installation footprint in the disposable recovery guest;
- requires installed `ISCC.exe` to report exact three-part version `6.7.1`;
- records `ISCC.exe` SHA-256 in `inno-setup-install-evidence.json`.

The offline step intentionally does not require live certificate-chain/revocation discovery. The executable trust decision was made on the connected acquisition host and is carried into recovery by the pinned immutable SHA-256 plus the acquisition manifest.

## Canonical installer builder enforcement

`tools/build_windows_installer.ps1` now fails closed if the selected `ISCC.exe` is not exact version `6.7.1`, including when an explicit `-IsccPath` is supplied.

For the P0.2 installer recovery run use the controlled compiler explicitly:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_windows_installer.ps1 `
  -PythonExecutable C:\P0_2_TOOLS\Python-3.12.10\python.exe `
  -IsccPath 'C:\P0_2_TOOLS\Inno-Setup-6.7.1\ISCC.exe'
```

The installer payload build manifest records:

- `inno_setup_version=6.7.1`;
- the SHA-256 of the exact `ISCC.exe` used.

A globally installed `6.7.2`, `6.7.3`, Inno Setup 7, or an unparseable compiler binary must be rejected rather than silently accepted.

## P0.2-B acceptance matrix

Repository/autonomous preparation is complete when all of these are true:

- exact `6.7.1` identity is locked;
- version-specific upstream acquisition path is locked;
- expected installer size and SHA-256 are locked;
- connected acquisition requires valid Authenticode from `Pyrsys B.V.`;
- detached upstream signature/public key/license are preserved in the controlled set;
- an offline portable install path exists and contains no network acquisition calls;
- canonical installer build rejects any compiler version other than `6.7.1`;
- compiler version and SHA-256 flow into build evidence;
- automated contract tests guard all of the above.

Real/local completion remains pending until all of these are true:

- exact upstream bytes are actually acquired and the verifier reports PASS;
- the complete verified set is archived under Arvectum control;
- an independent offline copy is produced and byte-matched;
- the exact verified set is staged into `ARVECTUM-P0-2-RECOVERY` without enabling networking;
- the offline install verifier reports exact `ISCC.exe` version `6.7.1`;
- the canonical Windows installer build completes while NIC remains `NONE`;
- before/after network-denial state and generated installer hash/evidence are exported;
- installer behavior/product contract is reconciled with the governed candidate.

## Completion discipline

Do not relabel P0.2-B or P0.2 as locally closed from repository code, documentation or hosted CI alone. This change makes the real execution deterministic and auditable; it does not replace the controlled artifact and endpoint-denied evidence boundary.
