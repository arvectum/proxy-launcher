@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PY_CMD="
where python >nul 2>nul
if not errorlevel 1 set "PY_CMD=python"
if defined PY_CMD goto :python_ready
where py >nul 2>nul
if not errorlevel 1 set "PY_CMD=py -3"
if defined PY_CMD goto :python_ready

echo Python 3 not found.
pause
exit /b 1

:python_ready
echo [1/4] Compiling sources...
%PY_CMD% -m py_compile proxy_core.py proxy_gui.py tests\test_proxy_core.py tests\test_release_scripts.py
if errorlevel 1 (
    echo Python compile check failed. Build aborted.
    pause
    exit /b 1
)

echo [2/4] Running unit tests...
%PY_CMD% -m unittest discover -v
if errorlevel 1 (
    echo Tests failed. Build aborted.
    pause
    exit /b 1
)

echo [3/4] Checking PyInstaller...
%PY_CMD% -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    %PY_CMD% -m pip install pyinstaller
    if errorlevel 1 (
        echo PyInstaller installation failed.
        pause
        exit /b 1
    )
)

echo [4/4] Building one-file EXE...
%PY_CMD% -m PyInstaller --noconfirm --clean --onefile --windowed --name "Arvectum Proxy Launcher" ^
    --version-file "version_info.txt" ^
    --icon "assets\arvectum.ico" ^
    --add-data "no_proxy.txt;." ^
    --add-data "proxy_settings.json;." ^
    --add-data "assets;assets" ^
    proxy_gui.py

if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Done: dist\Arvectum Proxy Launcher.exe
echo Copy dist\Arvectum Proxy Launcher.exe next to install.bat, then run install.bat.
pause
endlocal
