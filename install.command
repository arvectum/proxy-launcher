#!/bin/bash
# Arvectum Proxy Launcher - установка для macOS
set -u
cd "$(dirname "$0")"
APP_DIR="$HOME/Library/Application Support/ArvectumProxyLauncher"

echo "============================================"
echo "  Arvectum Proxy Launcher — установка"
echo "============================================"
echo

# ---------- 1. Копирование файлов ----------
echo "[1/4] Копирование файлов в $APP_DIR"
mkdir -p "$APP_DIR"
cp -f proxy_core.py proxy_gui.py start_proxy.sh stop_proxy.sh run_gui.sh restore_network.sh LICENSE "$APP_DIR" 2>/dev/null
    if [ -d tests ]; then cp -R tests "$APP_DIR/"; fi
if [ -d assets ]; then
    mkdir -p "$APP_DIR/assets"
    cp -f assets/* "$APP_DIR/assets/" 2>/dev/null
fi
# настройки и исключения не затираем при повторном запуске
[ -f "$APP_DIR/no_proxy.txt" ]        || cp -f no_proxy.txt "$APP_DIR/" 2>/dev/null
echo "        Готово."

# ---------- 2. Python + Tkinter ----------
echo "[2/4] Проверка Python..."
PY=python3
if ! command -v python3 >/dev/null 2>&1; then
    echo "        Python не найден."
    echo "        Установите:  xcode-select --install   (флаг: нужен Command Line Tools)"
    echo "        или скачайте Python с https://www.python.org/downloads/"
    echo
    read -r -p "        Открыть страницу python.org? [y/N] " yn
    if [ "$yn" = "y" ] || [ "$yn" = "Y" ]; then
        open "https://www.python.org/downloads/"
    fi
    exit 1
fi
if ! "$PY" -c "import tkinter" >/dev/null 2>&1; then
    echo "        В Python не хватает Tkinter."
    echo "        Установите:  brew install python-tk"
    exit 1
fi
echo "        Python: $("$PY" --version 2>&1)"

# ---------- 3. Автозапуск при входе (LaunchAgent) ----------
echo "[3/4] Настройка автозапуска..."
LAUNCH_PLIST="$HOME/Library/LaunchAgents/com.arvectum.proxylauncher.plist"
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$LAUNCH_PLIST" <<PLST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.arvectum.proxylauncher</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PY</string>
        <string>$APP_DIR/proxy_core.py</string>
        <string>--start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>ProcessType</key>
    <string>Background</string>
</dict>
</plist>
PLST
launchctl unload "$LAUNCH_PLIST" 2>/dev/null || true
launchctl load "$LAUNCH_PLIST" 2>/dev/null && echo "        Готово." || echo "        Автозапуск включён (загрузится при входе)."

# ---------- 4. Ярлык на рабочем столе ----------
echo "[4/4] Создание ярлыка на рабочем столе..."
cat > "$HOME/Desktop/Arvectum Proxy Launcher.command" <<'RUN'
#!/bin/bash
exec "~/Library/Application Support/ArvectumProxyLauncher/run_gui.sh"
RUN
chmod +x "$HOME/Desktop/Arvectum Proxy Launcher.command"
echo "        Готово."

echo
echo "============================================"
echo "  Установка завершена!"
echo
echo "  1) Данные прокси (IP, порт, логин, пароль)"
echo "     вводятся в открывшемся окне."
echo "  2) Прокси запускается автоматически"
echo "     при входе в систему."
echo "  3) Локальные сети и localhost — всегда в обход."
echo "============================================"
echo
"$PY" "$APP_DIR/proxy_gui.py"
