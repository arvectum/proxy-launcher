#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
[[ "$(uname -s)" == Darwin ]] || { echo "APL-MAC-005: macOS required" >&2; exit 2; }
app="${1:-dist/Arvectum Proxy Launcher.app}"
[[ -d "$app" ]] || { echo "Missing .app bundle: $app" >&2; exit 2; }
version="$(tr -d '[:space:]' < VERSION)"
arch="$(uname -m)"
out_dir="${2:-dist/dmg}"
mkdir -p "$out_dir"
stage="$(mktemp -d)"; trap 'rm -rf "$stage"' EXIT
cp -R "$app" "$stage/Arvectum Proxy Launcher.app"
cp LICENSE "$stage/LICENSE.txt"
cp THIRD_PARTY_NOTICES.txt "$stage/THIRD_PARTY_NOTICES.txt"
ln -s /Applications "$stage/Applications"
out="$out_dir/Arvectum_Proxy_Launcher-${version}-${arch}.dmg"
rm -f "$out"
/usr/bin/hdiutil create -quiet -volname "Arvectum Proxy Launcher" -srcfolder "$stage" -ov -format UDZO "$out"
/usr/bin/hdiutil verify "$out" >/dev/null
echo "$out"
