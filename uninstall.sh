#!/bin/bash
# Полное удаление Arvectum Proxy Launcher (Linux)
set -u
APP_DIR="$HOME/.local/share/ArvectumProxyLauncher"
AUTOSTART="$HOME/.config/autostart/arvectum-proxy.desktop"
DESKTOP_LNK="$HOME/Desktop/arvectum-proxy.desktop"

echo "============================================"
echo "  Arvectum Proxy Launcher — удаление"
echo "============================================"

echo "[1/3] Отключаю автозапуск..."
rm -f "$AUTOSTART"
echo "        Готово."

echo "[2/3] Снимаю системный прокси..."
if [ -f "$APP_DIR/stop_proxy.sh" ]; then
    bash "$APP_DIR/stop_proxy.sh" 2>/dev/null || true
fi
echo "        Готово."

echo "[3/3] Удаляю файлы и ярлык..."
rm -f "$DESKTOP_LNK"
rm -rf "$APP_DIR"
echo "        Готово."

echo
echo "  Прокси полностью удалён."
echo