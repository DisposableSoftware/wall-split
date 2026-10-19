#! /usr/bin/env nix-shell
#! nix-shell -i bash -p wtype jq grim imagemagick
# Spec: WIN-1, WIN-2, WIN-9, WIN-12.
# Run from the repo root after `nix build`, with no Wall Split windows open. Screenshots
# go to $OUT.
cd "$(dirname "$0")/../.." || exit 1
. scripts/manual/lib.sh
require_no_instance

T=$(mktemp -d); trap 'cleanup; rm -rf "$T"' EXIT
OUT=${OUT:-$T/shots}; mkdir -p "$OUT"
LOG=$T/app.log
magick -size 5120x1440 gradient:red-blue "$T/wide.png"
magick -size 3840x1080 gradient:green-yellow "$T/other.png"

launch
check "one window (WIN-1)" 1 "$(win_count)"
check "app ID (WIN-2)" "$APP" "$(active .class)"
check "title (WIN-1)" "Wall Split" "$(title)"
[ -n "${HEADLESS:-}" ] && check "default size in logical px (WIN-1)" "960 640" "$(size)"
check "no GTK version warning (WIN-1)" 0 "$(grep -c PyGIWarning "$LOG")"
shot "$OUT/empty.png"

"$BIN" "$T/wide.png" >/dev/null 2>&1
sleep 1
check "a file opens in the running window (WIN-9)" 1 "$(win_count)"
check "the title names the file (WIN-12)" "wide.png — Wall Split" "$(wins | jq -r '.[0].title')"
shot "$OUT/wide.png"
"$BIN" "$T/other.png" >/dev/null 2>&1
sleep 1
check "a second file reuses the window (WIN-9)" 1 "$(win_count)"
check "the title follows the new file (WIN-12)" "other.png — Wall Split" "$(wins | jq -r '.[0].title')"
shot "$OUT/other.png"

echo "screenshots in $OUT"
[ "$FAILS" = 0 ]
