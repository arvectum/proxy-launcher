@echo off
setlocal
chcp 65001 >nul
title Arvectum Proxy Launcher - Проверка релиза

echo Arvectum Proxy Launcher - проверка российского релиза
echo.

set "SCRIPT=%~dp0verify_russian_release.ps1"
if not exist "%SCRIPT%" (
  echo ОШИБКА: рядом с этим файлом не найден verify_russian_release.ps1
  echo.
  pause
  exit /b 1
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" -ReleaseDirectory "%~dp0"
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
