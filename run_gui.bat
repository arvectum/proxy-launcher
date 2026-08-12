@echo off
cd /d "%~dp0"
set "INSTALLED_EXE=%LOCALAPPDATA%\ArvectumProxyLauncher\Arvectum Proxy Launcher.exe"
if exist "%INSTALLED_EXE%" (
    start "" "%INSTALLED_EXE%"
) else if exist "%~dp0Arvectum Proxy Launcher.exe" (
    start "" "%~dp0Arvectum Proxy Launcher.exe"
) else if exist "%~dp0ProxyLauncher.exe" (
    start "" "%~dp0ProxyLauncher.exe"
) else (
    where pythonw >nul 2>nul
    if not errorlevel 1 (
        start "" pythonw.exe "%~dp0proxy_gui.py"
    ) else (
        echo Arvectum Proxy Launcher.exe / Python not found.
        pause
        exit /b 1
    )
)
