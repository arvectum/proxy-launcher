# [Win] P0.1 — Arvectum controlled-storage profile

Status: **DONE / P0.1 CLOSED 2026-08-17**

This document defines the completed controlled-storage perimeter for P0.1 and records the real primary/offline storage, round-trip verification and final human safe-eject evidence used to close the gate.

## Primary controlled perimeter

Primary storage is an Arvectum-controlled Mac mini using its internal storage. No public cloud or GitHub artifact is part of the perimeter.

Canonical root:

```text
/Users/Shared/Arvectum/ControlledArtifacts/ProxyLauncher/windows-build-inputs/
```

Each immutable input set is stored below a directory named by the full archive SHA-256:

```text
/Users/Shared/Arvectum/ControlledArtifacts/ProxyLauncher/windows-build-inputs/sha256-<FULL_ARCHIVE_SHA256>/
```

For the first P0.1 archive prepared from repository commit `74753f5fc78daf7484ce555922d5f7ac997fc138`, the governed archive SHA-256 is:

```text
4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886
```

Therefore its canonical primary directory is:

```text
/Users/Shared/Arvectum/ControlledArtifacts/ProxyLauncher/windows-build-inputs/sha256-4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886/
```

The governed transfer set is:

- `arvectum-windows-build-inputs-cpython-3.12.10-x64.zip`;
- `arvectum-windows-build-inputs-cpython-3.12.10-x64.zip.sha256`;
- `arvectum-windows-build-inputs-cpython-3.12.10-x64.zip.evidence.json`.

Final repository completion evidence is stored at `docs/evidence/P0_1_COMPLETION_EVIDENCE.json`.

A private SMB/SCP endpoint may be enabled temporarily for controlled transfer. Network endpoints are transport only; the canonical identifier in evidence is the Mac mini filesystem path plus archive SHA-256, not a transient IP address. Guest access and public Internet exposure are forbidden.

## Primary transfer evidence — PASS

Date: `2026-08-17`

The governed archive set was transferred from the Windows acquisition host to the Arvectum-controlled Mac mini over authenticated private-LAN SCP. No public cloud or GitHub artifact was used as the transfer source.

Recorded facts:

```text
windows_repository_commit = 50648e3711f2079b763d6b4a14a7297038628444
archive = arvectum-windows-build-inputs-cpython-3.12.10-x64.zip
archive_bytes = 30996168
archive_sha256 = 4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886
source_sidecar_present = YES
source_evidence_present = YES
source_canonical_offline_verifier = PASS
transport = authenticated private-LAN SCP
primary_zip_copied = YES
primary_sidecar_copied = YES
primary_evidence_copied = YES
primary_archive_bytes = 30996168
primary_archive_sha256 = 4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886
primary_byte_match_windows_source = YES
round_trip_canonical_verifier = PASS
primary_file_sealing = PASS
```

Canonical primary identifier:

```text
/Users/Shared/Arvectum/ControlledArtifacts/ProxyLauncher/windows-build-inputs/sha256-4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886/
```

## Primary sealing evidence — PASS

Date: `2026-08-17`

The exact three transferred source artifacts were sealed on the Arvectum-controlled Mac mini after an additional byte-identity check.

Recorded facts:

```text
mac_repository_commit = f8e420d0ecd2495afbd88b0dedb3a60435f95fd0
primary_archive_bytes = 30996168
primary_archive_sha256_before_seal = 4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886
primary_archive_sha256_after_seal = 4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886
primary_byte_identity_preserved = YES
zip_read_only = YES
zip_uchg = YES
sidecar_read_only = YES
sidecar_uchg = YES
evidence_read_only = YES
evidence_uchg = YES
primary_directory_world_writable = NO
access_policy_recorded = YES
retention_policy_recorded = YES
```

## Primary access policy

- Access is limited to authorized Arvectum administrator/operator accounts.
- Guest/anonymous access is disabled.
- Write permission is allowed only during controlled ingest or an explicitly approved maintenance operation.
- The three source artifacts are read-only and marked with the macOS user immutable flag (`uchg`).
- If file-sharing write access is enabled for ingest, it is removed or returned to read-only after verification.
- Any future replacement is stored under a new full-SHA256 directory. Existing verified bytes are not overwritten in place.
- Credentials, passwords, private keys and tokens must never be written into repository evidence.

An authorized administrator can deliberately clear `uchg`; therefore integrity remains anchored by the recorded SHA-256 and repeated verification, not by the filesystem flag alone.

## Retention policy

- Keep every controlled build-input set for as long as any supported Proxy Launcher release depends on it.
- After the last dependent release leaves support, retain that input set for at least **5 additional years** unless a later approved company retention policy requires longer storage.
- Deletion requires an explicit authorized Arvectum decision; it must never happen as part of ordinary cache cleanup, repository cleanup or workstation maintenance.
- The SHA-256, repository commit, release relationship and deletion decision record must outlive the deleted binary copy.

## Independent offline copy — PASS

The second copy is on a physically separate removable device that is disconnected after verification and stored separately from the Mac mini.

Governed volume label:

```text
ARVECTUM-1
```

`ARVECTUM-1` deliberately supersedes the earlier proposed `ARVECTUM-OFFLINE-01` label because the chosen exFAT formatting workflow required a shorter practical volume label. The shorter label is the canonical governed identifier for this physical copy.

The device is an external/removable `16.0 GB` exFAT volume. exFAT is accepted because integrity is anchored by SHA-256 and byte-for-byte comparison, and the cross-platform format allowed the final Windows round-trip verifier to read the device natively. Filesystem encryption is not a P0.1 integrity acceptance gate.

Canonical offline path used on macOS:

```text
/Volumes/ARVECTUM-1/ProxyLauncher/windows-build-inputs/sha256-4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886/
```

### Offline-copy creation/eject evidence — PASS

Date: `2026-08-17`

```text
offline_copy_execution_repository_commit = 8e5c87e01d085e1c085a2db1746e1c83ae4ff8b4
offline_physical_identifier_at_execution = /dev/disk4
offline_partition_identifier_at_execution = disk4s1
offline_device_label = ARVECTUM-1
offline_filesystem = exFAT
offline_capacity = 16.0 GB
offline_mount_point_before_eject = /Volumes/ARVECTUM-1
offline_external_removable = YES
offline_archive_bytes = 30996168
offline_archive_sha256 = 4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886
offline_zip_byte_match_primary = YES
offline_sidecar_byte_match_primary = YES
offline_evidence_byte_match_primary = YES
secrets_introduced = NO
sync_completed = YES
final_pre_eject_sha256 = 4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886
diskutil_eject = PASS
volume_mounted_after_eject = NO
physical_disconnection_after_creation = YES
```

The `/dev/disk4` and `disk4s1` identifiers were execution-time observations only and are not permanent device identities. The governed identity is the volume label `ARVECTUM-1`, the archive path and the exact archive SHA-256.

A continuously connected development/work SSD, another directory on the Mac mini, a GitHub artifact, Downloads/Desktop, or a synchronized public-cloud folder does **not** satisfy the independent offline-copy gate.

## Final Windows round-trip verification — PASS

Date: `2026-08-17`

Verification repository commit:

```text
1429e55959e9a3940b1f2e03e84f18fa7b05de0c
```

Offline copy on Windows:

```text
label = ARVECTUM-1
filesystem = exFAT
capacity = 16.0 GB
drive_letter_at_verification = D:
archive_bytes = 30996168
archive_sha256 = 4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886
canonical_windows_verifier = PASS
```

Fresh retrieval of Mac mini primary copy to Windows:

```text
retrieved_to = C:\Temp\proxy-launcher-p0-1-primary-roundtrip
archive_bytes = 30996168
archive_sha256 = 4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886
canonical_windows_verifier = PASS
```

Cross-copy comparison:

```text
zip_byte_match = YES
sidecar_byte_match = YES
evidence_byte_match = YES
```

The verifier was run with package-index access disabled in the process environment and with `-RequireCurrentRepositoryLocks`.

After final verification, the human operator safely ejected `ARVECTUM-1` from Windows, physically disconnected it and returned it to separate offline storage.

## First-archive identity

The completed P0.1 archive is bound to:

```text
repository_commit = 74753f5fc78daf7484ce555922d5f7ac997fc138
verification_repository_commit = 60c456aa90ef8c6269ca79fdde9ad5861ebb6398
final_roundtrip_repository_commit = 1429e55959e9a3940b1f2e03e84f18fa7b05de0c
archive = arvectum-windows-build-inputs-cpython-3.12.10-x64.zip
archive_bytes = 30996168
archive_sha256 = 4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886
cpython_installer_sha256 = 67b5635e80ea51072b87941312d00ec8927c4db9ba18938f7ad2d27b328b95fb
wheelhouse_hash_lock_sha256 = 6587ee8cc6e7528f3d86dcfcca16fb731b48102a7a24fc6f0f12363f79020943
wheel_count = 8
```

The earlier operator report that recorded `archive_bytes = 28737536` was incorrect metadata. The surviving archive reports `30996168` bytes, retains the governed SHA-256 above, and repeatedly passed the canonical verifier. It is the same SHA-addressed governed archive identity, not a replacement archive.

If a future archive is regenerated and its ZIP SHA-256 changes, do not silently substitute it for this instance. Re-run verification, create a new SHA256-named controlled directory and report the new identity explicitly.

## P0.1 closure

All required facts are now real and evidenced:

- primary canonical filesystem identifier: recorded;
- exact archive SHA-256: recorded and repeated across all copies;
- byte-match with acquisition source: **YES**;
- primary read-only/immutable sealing: **PASS**;
- access policy: **RECORDED**;
- retention policy: **RECORDED**;
- independent offline device `ARVECTUM-1`: **VERIFIED**;
- offline byte-match with primary: **YES**;
- physical disconnection after creation: **YES**;
- final Windows canonical verifier against offline bytes: **PASS**;
- final Windows canonical verifier against retrieved primary bytes: **PASS**;
- final safe eject and physical disconnect from Windows: **YES**;
- separate offline storage: **YES**;
- final evidence contains secrets: **NO**.

```text
P0.1 CLOSED: YES
```

Canonical completion record: `docs/evidence/P0_1_COMPLETION_EVIDENCE.json`.

The next roadmap action is `[Win] P0.2 — independent endpoint-denied sovereign recovery build`.
