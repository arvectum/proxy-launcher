#!/bin/bash
# Сборка одиночного Linux-приложения (PyInstaller). Запускать один раз на Linux.
set -e
cd "$(dirname "$0")"

PY=python3
if ! command -v pyinstaller >/dev/null 2>&1; then
    echo "Устанавливаю PyInstaller..."
    "$PY" -m pip install --user pyinstaller || "$PY" -m pip install --break-system-packages pyinstaller
fi

"$PY" -m PyInstaller --noconfirm --clean --onefile --windowed \
    --name "Arvectum Proxy Launcher" \
    --add-data "no_proxy.txt:." \
    --add-data "assets:assets" \
    --exclude-module "distutils" \
    linux_gui.py

echo
echo "Готово: dist/Arvectum Proxy Launcher"
echo "Запускайте приложение напрямую или через .desktop-ярлык."
