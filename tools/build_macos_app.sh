#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
[[ "$(uname -s)" == Darwin ]] || { echo "APL-MAC-004: macOS required" >&2; exit 2; }
python_bin="${PYTHON_BIN:-python3}"
"$python_bin" -m PyInstaller --version >/dev/null
icon="assets/arvectum.icns"
[[ -f "$icon" ]] || { echo "Missing canonical macOS icon: $icon" >&2; exit 2; }
rm -rf "dist/Arvectum Proxy Launcher.app" build/macos-app
"$python_bin" -m PyInstaller --noconfirm --clean --onedir --windowed \
  --name "Arvectum Proxy Launcher" \
  --osx-bundle-identifier "ru.arvectum.proxylauncher" \
  --icon "$icon" \
  --add-data "no_proxy.txt:." \
  --add-data "assets:assets" \
  --workpath build/macos-app \
  --specpath build/macos-app \
  proxy_gui.py
app="dist/Arvectum Proxy Launcher.app"
[[ -d "$app/Contents/MacOS" && -f "$app/Contents/Info.plist" ]] || { echo "Invalid .app bundle" >&2; exit 3; }
/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$app/Contents/Info.plist" | grep -qx 'ru.arvectum.proxylauncher'
echo "$app"
