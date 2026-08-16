@echo off
setlocal
chcp 65001 >nul
title Arvectum Proxy Launcher - Проверка релиза

echo Arvectum Proxy Launcher - проверка российского релиза
echo.

set "APL_VERIFY_SCRIPT=%~dp0verify_russian_release.ps1"
set "APL_VERIFY_DIR=%~dp0"
if not exist "%APL_VERIFY_SCRIPT%" (
  echo ОШИБКА: рядом с этим файлом не найден verify_russian_release.ps1
  echo.
  pause
  exit /b 1
)

rem Windows PowerShell 5.1 may treat UTF-8 .ps1 without BOM as ANSI.
rem Read the verifier explicitly as UTF-8 and compile it from Unicode text.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "$text=[System.IO.File]::ReadAllText($env:APL_VERIFY_SCRIPT,[System.Text.Encoding]::UTF8); $block=[ScriptBlock]::Create($text); & $block -ReleaseDirectory $env:APL_VERIFY_DIR"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo Проверка завершена успешно.
) else (
  echo Проверка завершилась ошибкой. Не запускайте файлы релиза.
)
echo.
pause
exit /b %RC%
