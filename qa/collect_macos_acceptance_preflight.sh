#!/usr/bin/env bash
set -euo pipefail

out="${1:-macos-acceptance-preflight.txt}"
dmg="${2:-}"
app="/Applications/Arvectum Proxy Launcher.app"
launchagent="$HOME/Library/LaunchAgents/ru.arvectum.proxylauncher.plist"
rollback="$HOME/Library/Application Support/Arvectum/ProxyLauncher/macos_proxy_backup.json"
mkdir -p "$(dirname "$out")" 2>/dev/null || true

{
  echo "APL-MAC-008 read-only preflight evidence"
  echo "collected_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "mutation=false"
  echo
  echo "== macOS =="
  /usr/bin/sw_vers 2>/dev/null || true
  echo "architecture=$(uname -m)"
  echo
  echo "== networksetup read-only capability =="
  if [[ -x /usr/sbin/networksetup ]]; then
    echo "networksetup=/usr/sbin/networksetup"
    services="$(/usr/sbin/networksetup -listallnetworkservices 2>/dev/null || true)"
    enabled_count="$(printf '%s\n' "$services" | sed '1d' | sed '/^\*/d;/^$/d' | wc -l | tr -d ' ')"
    disabled_count="$(printf '%s\n' "$services" | sed '1d' | grep -c '^\*' || true)"
    echo "enabled_network_service_count=$enabled_count"
    echo "disabled_network_service_count=$disabled_count"
  else
    echo "networksetup=unavailable"
  fi
  echo
  echo "== installed app =="
  if [[ -d "$app" ]]; then
    echo "app=present"
    plist="$app/Contents/Info.plist"
    /usr/bin/plutil -lint "$plist" 2>&1 || true
    /usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$plist" 2>/dev/null || true
    /usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$plist" 2>/dev/null || true
    /usr/bin/codesign --verify --deep --strict --verbose=2 "$app" 2>&1 || true
    /usr/bin/codesign -dv --verbose=2 "$app" 2>&1 || true
  else
    echo "app=missing"
  fi
  echo
  echo "== LaunchAgent =="
  if [[ -f "$launchagent" ]]; then
    echo "launchagent=present"
    /usr/bin/plutil -lint "$launchagent" 2>&1 || true
    /usr/libexec/PlistBuddy -c 'Print :Label' "$launchagent" 2>/dev/null || true
    /usr/libexec/PlistBuddy -c 'Print :RunAtLoad' "$launchagent" 2>/dev/null || true
  else
    echo "launchagent=missing"
  fi
  echo
  echo "== rollback evidence metadata only =="
  if [[ -e "$rollback" ]]; then
    echo "rollback_evidence=present"
    /usr/bin/stat -f 'mode=%Sp bytes=%z modified=%Sm' "$rollback" 2>/dev/null || true
  else
    echo "rollback_evidence=absent"
  fi
  if [[ -n "$dmg" ]]; then
    echo
    echo "== supplied DMG =="
    if [[ -f "$dmg" ]]; then
      /usr/bin/hdiutil verify "$dmg" 2>&1 || true
      /usr/bin/shasum -a 256 "$dmg" 2>/dev/null || true
    else
      echo "dmg=missing:$dmg"
    fi
  fi
  echo
  echo "NOTE: this collector is intentionally read-only. It never calls networksetup setters, launchctl bootstrap/bootout, installer, sudo, or proxy restore/mutation operations."
} > "$out"

printf '%s\n' "$out"
