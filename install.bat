@echo off
setlocal
if not defined ARVECTUM_APP_DIR set "ARVECTUM_APP_DIR=%USERPROFILE%\Documents\ArvectumProxyLauncher"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1" -Install -AppDir "%ARVECTUM_APP_DIR%" -SourceDir "%~dp0." -NonInteractive
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
    echo.
    echo Обновление не завершено. Предыдущая версия Launcher не была заменена.
    echo Настройки сети не изменены. Пришлите файл install.log из:
    echo %LOCALAPPDATA%\Arvectum\ProxyLauncher
    if not defined ARVECTUM_NONINTERACTIVE pause
)
exit /b %RC%
