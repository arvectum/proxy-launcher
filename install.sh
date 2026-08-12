#!/bin/bash
# Arvectum Proxy Launcher - установка для Linux (GNOME/GTK)
set -u
cd "$(dirname "$0")"
APP_DIR="$HOME/.local/share/ArvectumProxyLauncher"
AUTOSTART="$HOME/.config/autostart/arvectum-proxy.desktop"
DESKTOP_LNK="$HOME/Desktop/arvectum-proxy.desktop"

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
[ -f "$APP_DIR/no_proxy.txt" ]        || cp -f no_proxy.txt "$APP_DIR/" 2>/dev/null
[ -f "$APP_DIR/proxy_settings.json" ] || cp -f proxy_settings.json "$APP_DIR/" 2>/dev/null
echo "        Готово."

# ---------- 2. Python + Tkinter ----------
echo "[2/4] Проверка Python..."
PY=python3
if ! command -v python3 >/dev/null 2>&1; then
    echo "        Python не найден. Установите:  sudo apt install python3  (или dnf install python3)"
    exit 1
fi
if ! "$PY" -c "import tkinter" >/dev/null 2>&1; then
    echo "        В Python не хватает Tkinter. Установите:"
    echo "          Debian/Ubuntu: sudo apt install python3-tk"
    echo "          Fedora:        sudo dnf install python3-tkinter"
    exit 1
fi
echo "        Python: $("$PY" --version 2>&1)"

# ---------- 3. Автозапуск при входе (.desktop) ----------
echo "[3/4] Настройка автозапуска..."
mkdir -p "$(dirname "$AUTOSTART")"
cat > "$AUTOSTART" <<DESK
[Desktop Entry]
Type=Application
Name=Arvectum Proxy Launcher
Comment=Autostart Arvectum proxy on login
Exec=$PY $APP_DIR/proxy_core.py --start
Terminal=false
X-GNOME-Autostart-enabled=true
DESK
echo "        Готово."

# ---------- 4. Ярлык на рабочем столе ----------
echo "[4/4] Создание ярлыка на рабочем столе..."
icon="$APP_DIR/assets/arvectum-icon.png"
mkdir -p "$HOME/Desktop" 2>/dev/null || true
cat > "$DESKTOP_LNK" <<DESK
[Desktop Entry]
Type=Application
Name=Arvectum Proxy Launcher
Comment=Proxy launcher
Exec=$PY $APP_DIR/proxy_gui.py
Terminal=false
Icon=$icon
Categories=Network;
DESK
chmod +x "$DESKTOP_LNK" 2>/dev/null || true
chmod +x "$APP_DIR"/*.sh
echo "        Готово."

echo
echo "============================================"
echo "  Установка завершена!"
echo
echo "  1) Данные прокси (IP, порт, логин, пароль)"
echo "     вводятся в открывшемся окне."
echo "  2) Прокси запускается автоматически"
echo "     при входе в систему (GNOME: gsettings)."
echo "  3) Локальные сети и localhost — всегда в обход."
echo "============================================"
echo
"$PY" "$APP_DIR/proxy_gui.py"