@echo off
setlocal
if not defined ARVECTUM_APP_DIR set "ARVECTUM_APP_DIR=%USERPROFILE%\Documents\ArvectumProxyLauncher"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1" -Install -AppDir "%ARVECTUM_APP_DIR%" -SourceDir "%~dp0." -NonInteractive
exit /b %ERRORLEVEL%
