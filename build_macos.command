#!/bin/bash
# Сборка одиночного macOS-приложения (PyInstaller). Запускать один раз на macOS.
set -e
cd "$(dirname "$0")"

PY=python3
if ! command -v pyinstaller >/dev/null 2>&1; then
    echo "Устанавливаю PyInstaller..."
    "$PY" -m pip install --user pyinstaller || "$PY" -m pip install --break-system-packages pyinstaller
fi

# macOS требует .icns для иконки; получаем из assets/arvectum-icon.png
if [ ! -f assets/arvectum.icns ]; then
    echo "Генерирую assets/arvectum.icns из arvectum-icon.png..."
    mkdir -p /tmp/arvectum.iconset
    for s in 16 32 64 128 256 512 1024; do
        /usr/bin/sips -z "$s" "$s" assets/arvectum-icon.png --out "/tmp/arvectum.iconset/icon_${s}x${s}.png" >/dev/null 2>&1 || true
    done
    /usr/bin/iconutil -c icns /tmp/arvectum.iconset -o assets/arvectum.icns
fi

"$PY" -m PyInstaller --noconfirm --clean --onefile --windowed \
    --name "Arvectum Proxy Launcher" \
    --icon "assets/arvectum.icns" \
    --add-data "no_proxy.txt:." \
    --add-data "assets:assets" \
    --exclude-module "distutils" \
    proxy_gui.py

echo
echo "Готово: dist/Arvectum Proxy Launcher"
echo "Запускайте приложение двойным кликом, либо распространяйте один файл."
