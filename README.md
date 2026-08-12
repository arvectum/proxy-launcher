# Arvectum Proxy Launcher

Windows proxy launcher with local HTTP, HTTPS CONNECT, SOCKS5 and PAC support.

## Client release

The final client package is [release/Arvectum-Proxy-Launcher-Windows.zip](release/Arvectum-Proxy-Launcher-Windows.zip).

- ZIP SHA256: `C7E1CE047A274F309E3C9A7AF5CE82526161276070752AFD5CFFF35201AA6117`
- EXE SHA256: `E5044CE284A8B1FFEA2EB2288597CD338B7B248967E2FF8440D1C4A51367B1E5`

Unpack the archive and run `install.bat`. The installer places the application in `Documents\ArvectumProxyLauncher`, which is compatible with the Device Guard policy verified during acceptance.

Proxy credentials and runtime data are intentionally not versioned. Configure the upstream proxy on first launch.

## Development

Run `build_exe.bat` on Windows to compile and test the one-file EXE. The `tests/` directory contains proxy-core regression tests.

Интерфейс для управления системным прокси, с проверкой и настройкой исключений
