@echo off
setlocal enabledelayedexpansion

set "REPO_ROOT=%~dp0"
if "%REPO_ROOT:~-1%"=="\" set "REPO_ROOT=%REPO_ROOT:~0,-1%"
cd /d "%REPO_ROOT%"

where pwsh.exe >nul 2>&1
if %ERRORLEVEL% equ 0 (
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%REPO_ROOT%\tools\clean_build_windows.ps1" %*
    exit /b %ERRORLEVEL%
)

where powershell.exe >nul 2>&1
if %ERRORLEVEL% equ 0 (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%REPO_ROOT%\tools\clean_build_windows.ps1" %*
    exit /b %ERRORLEVEL%
)

echo [ERROR] PowerShell (pwsh or powershell.exe) is required to run the canonical build script.
exit /b 1
