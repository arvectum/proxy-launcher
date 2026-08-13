@echo off
setlocal EnableExtensions
chcp 65001 >nul
if not defined ARVECTUM_APP_DIR set "ARVECTUM_APP_DIR=%USERPROFILE%\Documents\ArvectumProxyLauncher"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" -AppDir "%ARVECTUM_APP_DIR%" -SourceDir "%~dp0"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" if not defined ARVECTUM_NONINTERACTIVE pause
exit /b %RC%
