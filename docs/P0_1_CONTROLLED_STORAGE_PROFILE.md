# [Win] P0.1 — Arvectum controlled-storage profile

Status: **PRIMARY + OFFLINE COPY VERIFIED / PHYSICAL DISCONNECTION + FINAL VERIFIER PENDING**

This document defines the concrete controlled-storage perimeter for P0.1. It does not itself close P0.1. Closure requires physical disconnection/separate storage of the verified removable copy, final canonical Windows verification and completion evidence described below.

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

The directory must contain exactly the transfer evidence set required by P0.1:

- `arvectum-windows-build-inputs-cpython-3.12.10-x64.zip`;
- `arvectum-windows-build-inputs-cpython-3.12.10-x64.zip.sha256`;
- `arvectum-windows-build-inputs-cpython-3.12.10-x64.zip.evidence.json`;
- final `P0_1_COMPLETION_EVIDENCE.json` after both controlled copies are proven.

A private SMB share may be enabled temporarily for transfer from the Windows acquisition host. Recommended share name:

```text
ArvectumControlledArtifacts
```

The SMB endpoint is transport only. The canonical identifier in evidence is the Mac mini filesystem path plus archive SHA-256, not a transient IP address. Guest access and public Internet exposure are forbidden.

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
round_trip_canonical_verifier = NOT_YET_RUN
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
offline_device_available_at_seal_time = NO
```

This closes the primary controlled-storage transfer, byte-match and post-ingest sealing sub-gates.

## Primary access policy

- Access is limited to authorized Arvectum administrator/operator accounts.
- Guest/anonymous access is disabled.
- Write permission is allowed only during controlled ingest or an explicitly approved maintenance operation.
- Immediately after byte verification, the three source artifacts are made read-only and marked with the macOS user immutable flag (`uchg`) where supported.
- If SMB write access was enabled for ingest, it is removed or the share is returned to read-only after verification.
- Any future replacement is stored under a new full-SHA256 directory. Existing verified bytes are not overwritten in place.
- Credentials, passwords, private keys and tokens must never be written into repository evidence.

Suggested post-verification protection on the Mac mini:

```bash
chmod 0444 <archive.zip> <archive.zip.sha256> <archive.zip.evidence.json>
chflags uchg <archive.zip> <archive.zip.sha256> <archive.zip.evidence.json>
```

The operator must record `ls -lO` output or equivalent evidence proving the resulting state. An authorized administrator can deliberately clear `uchg`; therefore integrity continues to be anchored by the recorded SHA-256 and repeated verification, not by the filesystem flag alone.

## Retention policy

- Keep every controlled build-input set for as long as any supported Proxy Launcher release depends on it.
- After the last dependent release leaves support, retain that input set for at least **5 additional years** unless a later approved company retention policy requires longer storage.
- Deletion requires an explicit authorized Arvectum decision; it must never happen as part of ordinary cache cleanup, repository cleanup or workstation maintenance.
- The SHA-256, repository commit, release relationship and deletion decision record must outlive the deleted binary copy.

## Independent offline copy

The second copy is on a physically separate removable device that must be disconnected after verification and stored separately from the Mac mini.

Governed volume label for the current physical offline device:

```text
ARVECTUM-1
```

`ARVECTUM-1` deliberately supersedes the earlier proposed `ARVECTUM-OFFLINE-01` label because the target filesystem/formatting workflow imposed a shorter practical volume-label constraint. The shorter label is the canonical governed identifier for this physical copy.

The current device is an external/removable `16.0 GB` exFAT volume. exFAT is accepted for this P0.1 copy because integrity is anchored by SHA-256 and byte-for-byte comparison, and the cross-platform format allows the final Windows round-trip verifier to read the device natively. Filesystem encryption is not a P0.1 integrity acceptance gate; operational secrets must never appear in Git or evidence.

Canonical offline path:

```text
/Volumes/ARVECTUM-1/ProxyLauncher/windows-build-inputs/sha256-<FULL_ARCHIVE_SHA256>/
```

For the current first archive:

```text
/Volumes/ARVECTUM-1/ProxyLauncher/windows-build-inputs/sha256-4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886/
```

## Independent offline-copy evidence — PASS (software verification/eject)

Date: `2026-08-17`

The governed three-file archive set was copied from the sealed Mac mini primary store to the physically separate removable volume and verified from the volume itself before software eject.

Recorded facts:

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
physical_disconnection = PENDING_HUMAN_OPERATOR
stored_separately_from_primary = PENDING_HUMAN_OPERATOR
```

The `/dev/disk4` and `disk4s1` identifiers are execution-time observations only and are not permanent device identities; they may change on future attachment. The governed identity is the volume label `ARVECTUM-1`, the canonical archive path and the exact archive SHA-256.

After software eject, the human operator must physically unplug `ARVECTUM-1` and store it separately from the Mac mini. After that human fact is confirmed, retrieve the exact offline bytes on Windows and run the canonical verifier.

A continuously connected development/work SSD, another directory on the Mac mini, a GitHub artifact, Downloads/Desktop, or a synchronized public-cloud folder does **not** satisfy the independent offline-copy gate.

## First-archive identity

The current P0.1 acceptance attempt is bound to:

```text
repository_commit = 74753f5fc78daf7484ce555922d5f7ac997fc138
verification_repository_commit = 60c456aa90ef8c6269ca79fdde9ad5861ebb6398
archive = arvectum-windows-build-inputs-cpython-3.12.10-x64.zip
archive_bytes = 30996168
archive_sha256 = 4a55f101bdd15a956c9bc4249fdbb694abadd682a3340c0f5ef08c174880a886
cpython_installer_sha256 = 67b5635e80ea51072b87941312d00ec8927c4db9ba18938f7ad2d27b328b95fb
wheelhouse_hash_lock_sha256 = 6587ee8cc6e7528f3d86dcfcca16fb731b48102a7a24fc6f0f12363f79020943
wheel_count = 8
```

The earlier operator report that recorded `archive_bytes = 28737536` was incorrect metadata. The surviving local archive reports `30996168` bytes, retains the exact same governed SHA-256 above, and passed `tools/verify_windows_build_input_archive.ps1 -RequireCurrentRepositoryLocks` at repository commit `60c456aa90ef8c6269ca79fdde9ad5861ebb6398`. Therefore this is the same SHA-addressed governed archive identity; it is not a replacement archive and must not be marked lost or retired.

If the local archive is regenerated and its ZIP SHA-256 changes, do not silently substitute it for this instance. Re-run local verification, create a new SHA256-named controlled directory and report the new identity explicitly.

## Required evidence before P0.1 may close

Primary controlled storage must report:

- host role: `Arvectum-controlled Mac mini`;
- canonical filesystem identifier;
- exact archive SHA-256;
- byte-match with acquisition host: `YES`;
- archive verification: `PASS`;
- access policy recorded: `YES`;
- retention policy recorded: `YES`;
- post-ingest files protected/read-only: `YES`.

Independent offline copy must report:

- device label `ARVECTUM-1`;
- canonical filesystem identifier;
- exact archive SHA-256;
- byte-match with primary: `YES`;
- physically disconnected after verification: `YES`;
- stored separately from the primary Mac mini: `YES`.

Final verification must report canonical Windows verifier **PASS** against the exact controlled/retrieved bytes and final `P0_1_COMPLETION_EVIDENCE.json` must contain no secrets.

Only after all of those facts are real and evidenced may the final record state:

```text
P0.1 CLOSED: YES
```

The next roadmap action is then `[Win] P0.2 — independent endpoint-denied sovereign recovery build`.
