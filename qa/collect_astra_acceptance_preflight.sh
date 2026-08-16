#!/usr/bin/env bash
set -euo pipefail

out="${1:-astra-acceptance-preflight.txt}"
mkdir -p "$(dirname "$out")" 2>/dev/null || true

{
  echo "APL-LNX-010 read-only preflight evidence"
  echo "collected_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "mutation=false"
  echo
  echo "== kernel =="
  uname -a || true
  echo
  echo "== /etc/os-release =="
  cat /etc/os-release 2>/dev/null || echo "unavailable"
  echo
  echo "== Astra release marker =="
  if [[ -r /etc/astra_version ]]; then cat /etc/astra_version; else echo "unavailable"; fi
  echo
  echo "== NetworkManager =="
  if command -v nmcli >/dev/null 2>&1; then
    command -v nmcli
    nmcli --version || true
    echo "active_connection_count=$(nmcli -t -f UUID connection show --active 2>/dev/null | sed '/^$/d' | wc -l | tr -d ' ')"
  else
    echo "nmcli=unavailable"
  fi
  if command -v systemctl >/dev/null 2>&1; then
    echo "NetworkManager.service=$(systemctl is-active NetworkManager.service 2>/dev/null || true)"
  fi
  echo
  echo "== installed package =="
  if command -v dpkg-query >/dev/null 2>&1; then
    dpkg-query -W -f='status=${db:Status-Status}\nversion=${Version}\narchitecture=${Architecture}\n' arvectum-proxy-launcher 2>/dev/null || echo "package=not-installed"
  else
    echo "dpkg-query=unavailable"
  fi
  echo
  echo "== installed payload =="
  app='/opt/arvectum-proxy-launcher/Arvectum Proxy Launcher'
  launcher='/usr/bin/arvectum-proxy-launcher'
  desktop='/usr/share/applications/arvectum-proxy-launcher.desktop'
  icon='/usr/share/icons/hicolor/256x256/apps/arvectum-proxy-launcher.png'
  for path in "$app" "$launcher" "$desktop" "$icon"; do
    if [[ -e "$path" ]]; then
      printf 'present=%s\n' "$path"
      if [[ -f "$path" ]] && command -v sha256sum >/dev/null 2>&1; then sha256sum "$path"; fi
    else
      printf 'missing=%s\n' "$path"
    fi
  done
  echo
  echo "== desktop session =="
  echo "XDG_SESSION_TYPE=${XDG_SESSION_TYPE:-unknown}"
  echo "XDG_CURRENT_DESKTOP=${XDG_CURRENT_DESKTOP:-unknown}"
  echo "DISPLAY_present=$([[ -n "${DISPLAY:-}" ]] && echo yes || echo no)"
  echo "WAYLAND_DISPLAY_present=$([[ -n "${WAYLAND_DISPLAY:-}" ]] && echo yes || echo no)"
  echo
  echo "NOTE: this collector is intentionally read-only. It does not call nmcli connection modify, sudo, pkexec, install/remove packages, or start the application."
} > "$out"

printf '%s\n' "$out"
