# Arvectum Proxy Launcher

Arvectum Proxy Launcher is a local proxy launcher with a Windows graphical client. It exposes local HTTP, SOCKS5 and PAC endpoints and routes normal traffic through a configured upstream HTTP proxy; `no_proxy.txt` entries go direct.

## Current canonical status

Windows **0.2.3 P0.2** is the verified release track. It uses a canonical executable handoff in `%USERPROFILE%\Documents\ArvectumProxyLauncher`, keeps mutable state in `%LOCALAPPDATA%\Arvectum\ProxyLauncher`, protects saved upstream passwords with current-user Windows DPAPI, and includes rollback/recovery and process-ownership safeguards.

macOS and Linux scripts and packaging assets are retained for further integration. They are not currently CI-verified against the Windows 0.2.3 safety architecture, so they must not be represented as production-ready releases.

## Build and test

```powershell
python -m py_compile proxy_core.py proxy_gui.py
python -m unittest discover -s tests -v
```

On Windows, run `build_exe.bat` to build the portable executable. CI builds the portable artifact, validates a copy launched from the canonical Documents path, verifies SHA-256, and uploads the ZIP as a GitHub Actions artifact.

## Configuration and recovery

User runtime configuration is created on first use under LocalAppData and is deliberately excluded from Git. No `proxy_settings.json` is bundled in source or CI artifacts. The application supplies safe defaults programmatically; enter upstream host and credentials in the GUI. Passwords are stored through DPAPI, never as plaintext settings on Windows.

Do not manually remove recovery files while the proxy is active. Use the launcher’s recovery action or `restore_network.bat` if the GUI is unavailable.

## Releases

The `release/` directory contains only supporting documentation. Obtain executables from GitHub Releases or CI artifacts; historical ZIPs remain reachable through Git history but are not canonical release inputs.

## License and contribution

See [LICENSE](LICENSE), [SECURITY](SECURITY), [CONTRIBUTING](CONTRIBUTING), and [CODE_OF_CONDUCT](CODE_OF_CONDUCT).
