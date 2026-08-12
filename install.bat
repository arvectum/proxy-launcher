@echo off
setlocal EnableExtensions
chcp 65001 >nul

if not defined ARVECTUM_APP_DIR set "ARVECTUM_APP_DIR=%USERPROFILE%\Documents\ArvectumProxyLauncher"
set "APP_DIR=%ARVECTUM_APP_DIR%"
set "APP_EXE=Arvectum Proxy Launcher.exe"
set "SHORTCUT=Arvectum Proxy Launcher.lnk"
set "PYDIR="
set "PYWIN="

echo ============================================
echo   Arvectum Proxy Launcher — установка
echo ============================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "[void][System.IO.Directory]::CreateDirectory($env:ARVECTUM_APP_DIR)" >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: не удалось создать каталог приложения.
    echo Проверьте Controlled Folder Access / Device Guard Windows.
    if not defined ARVECTUM_NONINTERACTIVE pause
    exit /b 1
)

rem Безопасное обновление поверх предыдущей версии: сначала остановить её
rem и убрать старую задачу автозапуска. После установки автозапуск можно
rem включить заново из GUI после проверки upstream.
if exist "%APP_DIR%\%APP_EXE%" (
    "%APP_DIR%\%APP_EXE%" --stop >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ОШИБКА: предыдущую версию не удалось безопасно остановить/откатить.
        echo Установка отменена, чтобы не потерять резервные копии сети.
        echo Запустите restore_network.bat и повторите установку.
        echo.
        pause
        exit /b 1
    )

)
if exist "%APP_DIR%\proxy_internet_backup.json" (
    echo ОШИБКА: осталась резервная копия WinINET после остановки. Установка отменена.
    pause
    exit /b 1
)
if exist "%APP_DIR%\proxy_env_backup.json" (
    echo ОШИБКА: осталась резервная копия proxy environment после остановки. Установка отменена.
    pause
    exit /b 1
)
schtasks /Delete /F /TN "ArvectumProxyLauncher" >nul 2>&1

rem ------------------------------------------------------------
rem Предпочтительный путь: готовый one-file EXE рядом с installer.
rem ------------------------------------------------------------
if exist "%~dp0%APP_EXE%" goto :install_exe

echo Готовый "%APP_EXE%" рядом с install.bat не найден.
echo Устанавливаю исходную Python-версию как резервный вариант.
echo.

echo [1/3] Копирование файлов в %APP_DIR%
for %%F in (proxy_core.py proxy_gui.py start_proxy.bat stop_proxy.bat run_gui.bat restore_network.bat README.md INSTALL.txt install.bat uninstall.bat) do (
    if exist "%~dp0%%F" copy /y "%~dp0%%F" "%APP_DIR%\" >nul
)
if exist "%~dp0assets" xcopy /e /y /i "%~dp0assets" "%APP_DIR%\assets" >nul
if not exist "%APP_DIR%\no_proxy.txt"        copy /y "%~dp0no_proxy.txt"        "%APP_DIR%\" >nul
if not exist "%APP_DIR%\proxy_settings.json" copy /y "%~dp0proxy_settings.json" "%APP_DIR%\" >nul
echo        Готово.

echo [2/3] Проверка Python...
where py >nul 2>nul
if not errorlevel 1 goto :found_py
where python >nul 2>nul
if not errorlevel 1 goto :found_python
goto :install_python

:found_py
for /f "tokens=*" %%i in ('py -3 -c "import sys;print(sys.executable)"') do set "PYDIR=%%~dpi"
goto :have_python

:found_python
for /f "tokens=*" %%i in ('python -c "import sys;print(sys.executable)"') do set "PYDIR=%%~dpi"

:have_python
if defined PYDIR set "PYWIN=%PYDIR%pythonw.exe"
if defined PYWIN if exist "%PYWIN%" goto :python_ok
set "PYWIN="

:install_python
echo        Python не найден — пробую установить через winget...
where winget >nul 2>nul
if errorlevel 1 goto :python_failed
winget install -e --id Python.Python.3.12 --scope user --accept-source-agreements --accept-package-agreements
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\*") do (
    if exist "%%~fD\pythonw.exe" set "PYWIN=%%~fD\pythonw.exe"
)
if defined PYWIN goto :python_ok

:python_failed
echo.
echo   ОШИБКА: не удалось найти или установить Python.
echo   Для клиентской поставки рекомендуется положить готовый
echo   "%APP_EXE%" рядом с install.bat и запустить установку снова.
echo.
pause
exit /b 1

:python_ok
echo        Python: %PYWIN%
echo [3/3] Создание ярлыка...
>  "%TEMP%\mklnk.ps1" echo $lnk = ^(New-Object -ComObject WScript.Shell^).CreateShortcut^([Environment]::GetFolderPath^('Desktop'^) + '\%SHORTCUT%'^)
>> "%TEMP%\mklnk.ps1" echo $lnk.TargetPath = '%PYWIN%'
>> "%TEMP%\mklnk.ps1" echo $lnk.Arguments = '"%APP_DIR%\proxy_gui.py"'
>> "%TEMP%\mklnk.ps1" echo $lnk.WorkingDirectory = '%APP_DIR%'
>> "%TEMP%\mklnk.ps1" echo $lnk.IconLocation = '%APP_DIR%\assets\arvectum.ico'
>> "%TEMP%\mklnk.ps1" echo $lnk.Save^(^)
powershell -NoProfile -ExecutionPolicy Bypass -File "%TEMP%\mklnk.ps1" >nul 2>&1
del "%TEMP%\mklnk.ps1" >nul 2>nul
goto :finish_python

:install_exe
echo [1/2] Установка готового приложения в %APP_DIR%
set "ARVECTUM_SOURCE=%~dp0%APP_EXE%"
set "ARVECTUM_DESTINATION=%APP_DIR%\%APP_EXE%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Copy-Item -LiteralPath $env:ARVECTUM_SOURCE -Destination $env:ARVECTUM_DESTINATION -Force -ErrorAction Stop" >nul 2>&1
if errorlevel 1 goto :copy_exe_failed
if not exist "%APP_DIR%\%APP_EXE%" goto :copy_exe_failed
goto :copy_exe_done

:copy_exe_failed
    echo ОШИБКА: не удалось скопировать приложение.
    pause
    exit /b 1

:copy_exe_done
set "ARVECTUM_UNINSTALL_SOURCE=%~dp0uninstall.bat"
set "ARVECTUM_RESTORE_SOURCE=%~dp0restore_network.bat"
set "ARVECTUM_UNINSTALL_PS_SOURCE=%~dp0uninstall.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Copy-Item -LiteralPath $env:ARVECTUM_UNINSTALL_SOURCE -Destination $env:ARVECTUM_APP_DIR -Force -ErrorAction Stop" >nul 2>&1
if errorlevel 1 goto :copy_aux_failed
powershell -NoProfile -ExecutionPolicy Bypass -Command "Copy-Item -LiteralPath $env:ARVECTUM_RESTORE_SOURCE -Destination $env:ARVECTUM_APP_DIR -Force -ErrorAction Stop" >nul 2>&1
if errorlevel 1 goto :copy_aux_failed
powershell -NoProfile -ExecutionPolicy Bypass -Command "Copy-Item -LiteralPath $env:ARVECTUM_UNINSTALL_PS_SOURCE -Destination $env:ARVECTUM_APP_DIR -Force -ErrorAction Stop" >nul 2>&1
if errorlevel 1 goto :copy_aux_failed
goto :copy_aux_done

:copy_aux_failed
    echo ОШИБКА: не удалось скопировать служебные файлы установки.
    if not defined ARVECTUM_NONINTERACTIVE pause
    exit /b 1

:copy_aux_done
echo        Готово.

echo [2/2] Создание ярлыка...
>  "%TEMP%\mklnk.ps1" echo $lnk = ^(New-Object -ComObject WScript.Shell^).CreateShortcut^([Environment]::GetFolderPath^('Desktop'^) + '\%SHORTCUT%'^)
>> "%TEMP%\mklnk.ps1" echo $lnk.TargetPath = '%APP_DIR%\%APP_EXE%'
>> "%TEMP%\mklnk.ps1" echo $lnk.WorkingDirectory = '%APP_DIR%'
>> "%TEMP%\mklnk.ps1" echo $lnk.IconLocation = '%APP_DIR%\%APP_EXE%,0'
>> "%TEMP%\mklnk.ps1" echo $lnk.Save^(^)
powershell -NoProfile -ExecutionPolicy Bypass -File "%TEMP%\mklnk.ps1" >nul 2>&1
del "%TEMP%\mklnk.ps1" >nul 2>nul

echo.
echo ============================================
echo   Установка завершена.
echo   Сейчас откроется окно настройки прокси.
echo   Автозапуск включайте в приложении ПОСЛЕ
echo   заполнения и проверки внешнего прокси.
echo ============================================
echo.
start "" "%APP_DIR%\%APP_EXE%"
endlocal
exit /b 0

:finish_python
echo.
echo ============================================
echo   Установка завершена.
echo   Сейчас откроется окно настройки прокси.
echo   Автозапуск включайте в приложении ПОСЛЕ
echo   заполнения и проверки внешнего прокси.
echo ============================================
echo.
start "" "%PYWIN%" "%APP_DIR%\proxy_gui.py"
endlocal
exit /b 0
