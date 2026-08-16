#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
source tools/appimage-toolchain.lock
cache="${APPIMAGE_TOOLCHAIN_CACHE:-$repo_root/.cache/appimage}"
mkdir -p "$cache"
fetch() {
  local url="$1" out="$2" sha="$3"
  if [[ ! -f "$out" ]] || ! echo "$sha  $out" | sha256sum -c - >/dev/null 2>&1; then
    rm -f "$out"
    curl --fail --location --retry 3 --silent --show-error "$url" --output "$out"
  fi
  echo "$sha  $out" | sha256sum -c -
}
fetch "$APPIMAGETOOL_URL" "$cache/appimagetool-x86_64.AppImage" "$APPIMAGETOOL_SHA256"
fetch "$APPIMAGE_RUNTIME_URL" "$cache/runtime-x86_64" "$APPIMAGE_RUNTIME_SHA256"
chmod 0755 "$cache/appimagetool-x86_64.AppImage"
printf '%s\n' "$cache/appimagetool-x86_64.AppImage" "$cache/runtime-x86_64"
