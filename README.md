# Arvectum Proxy Launcher

Arvectum Proxy Launcher is a local proxy launcher with a Windows graphical client. It exposes local HTTP, SOCKS5 and PAC endpoints and routes normal traffic through a configured upstream HTTP proxy; `no_proxy.txt` entries go direct.

## Current canonical status

Windows **0.2.3** is the verified release track. It uses a canonical executable handoff in `%USERPROFILE%\Documents\ArvectumProxyLauncher`, keeps mutable state in `%LOCALAPPDATA%\Arvectum\ProxyLauncher`, protects saved upstream passwords with current-user Windows DPAPI, and includes rollback/recovery and process-ownership safeguards.

Windows Portable and Windows Installer are separate production release tracks built from the same application binary and canonical `VERSION`. The installer is `Arvectum-Proxy-Launcher-X.Y.Z-windows-x64-setup.exe`; build it locally after the portable build with `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build_windows_installer.ps1`. Code signing is not included in this release track.

macOS and Linux scripts and packaging assets are retained for further integration. They are not currently CI-verified against the Windows 0.2.3 safety architecture, so they must not be represented as production-ready releases.

## Versioning and releases

See [RELEASE_POLICY.md](RELEASE_POLICY.md) for canonical release, versioning, tag, artifact naming, and checksum policies.

* **Current product version:** `0.2.3` (canonical SemVer).
* **Engineering milestone:** `P0.2` (internal planning milestone, not part of the product version).
* **Verified platform track:** Windows `0.2.3` is verified; macOS and Linux remain in progress.
* **Release distribution:** Official releases are created by release automation on verified SemVer tags (`vX.Y.Z`) and published to **GitHub Releases**.
* **CI artifacts:** GitHub Actions builds provide QA and pre-release verification packages. Manual release workflow runs execute as dry-runs only.

## Build and test

### Canonical Windows Clean Build

Prerequisites: Windows x64 with Python 3.12.10 x64.

To run a fully isolated, clean, reproducible build:

PowerShell (pwsh):
```powershell
pwsh -NoProfile -File .\tools\clean_build_windows.ps1
```

Windows PowerShell:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\clean_build_windows.ps1
```

Or via compatibility wrapper:
```cmd
build_exe.bat
```

Build outputs:
* `out/Arvectum-Proxy-Launcher-0.2.3-windows-x64-portable.zip` — canonical portable package
* `out/SHA256SUMS.txt` — external SHA-256 package checksum manifest
* `out/build-result.json` — build metadata and provenance manifest

### Source Testing

```powershell
python -m py_compile proxy_core.py proxy_gui.py
python -m unittest discover -s tests -v
```

## Configuration and recovery

User runtime configuration is created on first use under LocalAppData and is deliberately excluded from Git. No `proxy_settings.json` is bundled in source or CI artifacts. Settings use a versioned, validated schema; writes are same-directory atomic replacements with flush/fsync, and the previous valid configuration is retained as an encrypted last-known-good snapshot. Structurally corrupted settings are quarantined and recovered from that snapshot when possible, otherwise the application uses programmatic safe defaults without silently trusting malformed data. Upstream credentials are stored through current-user Windows DPAPI and are never written as plaintext by the Windows release track.

Do not manually remove recovery files while the proxy is active. Use the launcher’s recovery action or `restore_network.bat` if the GUI is unavailable.

## Releases

The `release/` directory contains only supporting documentation. Obtain executables from GitHub Releases or CI artifacts; historical ZIPs remain reachable through Git history but are not canonical release inputs.

## License and contribution

See [LICENSE](LICENSE), [SECURITY](SECURITY), [CONTRIBUTING](CONTRIBUTING), and [CODE_OF_CONDUCT](CODE_OF_CONDUCT).
