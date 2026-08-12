@echo off
setlocal EnableExtensions
if not defined ARVECTUM_APP_DIR set "ARVECTUM_APP_DIR=%USERPROFILE%\Documents\ArvectumProxyLauncher"
set "SCRIPT=%~dp0uninstall.ps1"
if not exist "%SCRIPT%" (
    echo ERROR: uninstall.ps1 is missing.
    pause
    exit /b 1
)

if defined ARVECTUM_NONINTERACTIVE (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" -AppDir "%ARVECTUM_APP_DIR%" -NonInteractive
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" -AppDir "%ARVECTUM_APP_DIR%"
)
exit /b %ERRORLEVEL%
