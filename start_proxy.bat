@echo off
cd /d "%~dp0"
set "INSTALLED_EXE=%USERPROFILE%\Documents\ArvectumProxyLauncher\Arvectum Proxy Launcher.exe"
if exist "%INSTALLED_EXE%" (
    start "" "%INSTALLED_EXE%" --start
) else if exist "%~dp0Arvectum Proxy Launcher.exe" (
    start "" "%~dp0Arvectum Proxy Launcher.exe" --start
) else if exist "%~dp0ProxyLauncher.exe" (
    start "" "%~dp0ProxyLauncher.exe" --start
) else (
    where pythonw >nul 2>nul
    if not errorlevel 1 (
        start "" pythonw.exe "%~dp0proxy_core.py" --start
    ) else (
        echo Arvectum Proxy Launcher.exe / Python not found.
        pause
        exit /b 1
    )
)
