# Release and Version Policy

## 1. Canonical Repository and Sources

* **Canonical source of truth:** GitHub repository [`arvectum/proxy-launcher`](https://github.com/arvectum/proxy-launcher).
* **Canonical integration branch:** `main`.
* **Mirrors:** External mirrors (e.g., GitVerse) are downstream mirrors and do not serve as an independent source of truth.
* **Release binaries:** Pre-built binary archives (ZIP, EXE, DMG, tarball) committed directly into Git are historical artifacts only and are **not** canonical release distribution sources.

## 2. Versioning Scheme

Arvectum Proxy Launcher strictly follows **Semantic Versioning (SemVer 2.0.0)**:

```text
MAJOR.MINOR.PATCH
```

* **MAJOR:** Incompatible architectural shifts or breaking public contract changes (after 1.0.0).
* **MINOR:** New user features, capabilities, or verified platform support.
* **PATCH:** Bug fixes, security hotfixes, recovery stabilization, or packaging corrections without new functional scope.

While product versions are below `1.0.0` (e.g. `0.2.3`), minor releases may contain non-backward-compatible improvements, accompanied by mandatory release notes.

### Current Version Status
* **Canonical Product Version:** `0.2.3`
* The presence of a version number in code or documentation indicates the software version baseline, **not** that a public release has already been published.

## 3. Engineering Milestones vs. Product Versions

Engineering milestones and backlog markers (such as `P0`, `P0.2`, `P0.4`, `RC2`, `final`, `latest`, `fixed`) represent internal project planning and QA milestones.

**Rules:**
* Engineering milestones are strictly internal metadata.
* Milestones are **never** part of the canonical product version string.
* Milestones must not be embedded in:
  * Public Git tags (`v0.2.3`, not `v0.2.3-P0.2` or `0.2.3 P0.2`).
  * GitHub Release titles or tags.
  * Windows executable metadata (`ProductVersion`, `FileVersion`).
  * Canonical release artifact filenames.
* Valid prerelease identifiers follow SemVer specifications only (e.g., `0.2.4-rc.1`, `0.3.0-beta.1`).

## 4. Git Tags

* **Stable releases:** `vX.Y.Z` (e.g., `v0.2.3`, `v0.2.4`, `v0.3.0`).
* **Prerelease builds:** `vX.Y.Z-prerelease.N` (e.g., `v0.2.4-rc.1`, `v0.3.0-beta.1`).

**Tag Rules:**
1. Release tags are **immutable**. Once published, a tag must never be moved or replaced.
2. Release tags must point directly to a commit on `main` that has green CI status.
3. If an issue is discovered after tagging/releasing, do not modify the tag; issue a new `PATCH` release.

## 5. Canonical Release Pipeline

Canonical distribution flow:
```text
source change
  -> Pull Request
  -> main
  -> green CI
  -> version consistency validation
  -> Git tag (vX.Y.Z)
  -> CI release build
  -> SHA256SUMS.txt generation
  -> GitHub Release
```

* **Developer workstation builds:** Binaries built on developer workstations are strictly for local testing and debugging. They are not canonical release artifacts.
* **CI Artifacts vs. GitHub Releases:** GitHub Actions artifacts are temporary QA and pre-release test builds. GitHub Releases is the canonical public binary distribution channel.

## 6. Canonical Artifact Naming

Standard release filenames:

* **Windows Portable:** `Arvectum-Proxy-Launcher-X.Y.Z-windows-x64-portable.zip`
* **Windows Installer:** `Arvectum-Proxy-Launcher-X.Y.Z-windows-x64-setup.exe`
* **macOS Apple Silicon:** `Arvectum-Proxy-Launcher-X.Y.Z-macos-arm64.dmg`
* **macOS Intel:** `Arvectum-Proxy-Launcher-X.Y.Z-macos-x64.dmg` (when supported)
* **Linux x86_64:** `Arvectum-Proxy-Launcher-X.Y.Z-linux-x86_64.tar.gz`
* **Checksum Manifest:** `SHA256SUMS.txt`

## 7. Checksum Manifest Policy

* Release checksums must be published in standard `SHA256SUMS.txt` format:
  ```text
  <sha256>  <filename>
  ```
* For GitHub Releases, `SHA256SUMS.txt` must cover all final downloadable release packages (ZIP, EXE, DMG, tar.gz) and portable executables.

## 8. Platform Release Maturity

* **Windows (0.2.3):** Verified production track with Documents handoff, LocalAppData isolation, DPAPI credential protection, rollback/recovery, and process-ownership enforcement.
* **macOS:** Retained for continued development; not verified for production release until dedicated CI build and verification gates are implemented.
* **Linux:** Retained for continued development; not verified for production release until dedicated CI build and verification gates are implemented.
