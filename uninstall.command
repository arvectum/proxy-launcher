#!/bin/bash
# Полное удаление Arvectum Proxy Launcher (macOS)
set -u
APP_DIR="$HOME/Library/Application Support/ArvectumProxyLauncher"
LAUNCH_PLIST="$HOME/Library/LaunchAgents/com.arvectum.proxylauncher.plist"
DESKTOP_LNK="$HOME/Desktop/Arvectum Proxy Launcher.command"

echo "============================================"
echo "  Arvectum Proxy Launcher — удаление"
echo "============================================"

echo "[1/3] Отключаю автозапуск..."
launchctl unload "$LAUNCH_PLIST" 2>/dev/null || true
rm -f "$LAUNCH_PLIST"
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