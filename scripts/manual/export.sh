#! /usr/bin/env nix-shell
#! nix-shell -i bash -p wtype jq grim imagemagick
# Spec: EXP-1, EXP-2, EXP-3, PROD-4.
# Run from the repo root after `nix build`, with no Wall Split windows open. Loads a
# 5120×1440 image, exports it as wall.png through the save dialog, and compares the two
# outputs with the source. Then exports into a read-only directory and screenshots the
# error alert.
cd "$(dirname "$0")/../.." || exit 1
. scripts/manual/lib.sh
require_no_instance

T=$(mktemp -d); trap 'cleanup; chmod -R u+w "$T"; rm -rf "$T"' EXIT
OUT=${OUT:-$T/shots}; mkdir -p "$OUT" "$T/out" "$T/locked"
magick -size 5120x1440 plasma:fractal -alpha off -depth 8 "$T/src.png"
chmod a-w "$T/locked"

# The save dialog's app ID is the program name, "wall-split", not $APP.
all_wins() { if [ -n "${HEADLESS:-}" ]; then sway_wins; else hyprctl clients -j; fi | jq "[.[] | select(.class==\"$APP\" or .class==\"wall-split\")]"; }
dialog_keys() {
  case "$(active .class)" in
    "$APP" | wall-split) ;;
    *) echo "focus left Wall Split; stopping so keys don't go to another app" >&2; cleanup; exit 3 ;;
  esac
  if [ -n "${HEADLESS:-}" ]; then wtype -d 100 -k Shift_L "$@"; else wtype -d 100 "$@"; fi
  sleep 0.6
}

# export_to PATH: opens Export (the fourth Tab stop, after Split and Crop) and saves as PATH.
export_to() {
  focus_app; sleep 0.3
  keys -k Tab -k Tab -k Tab -k Tab
  keys -k space
  sleep 1
  check "the save dialog opened" 2 "$(all_wins | jq length)"
  dialog_keys -M ctrl a -m ctrl
  dialog_keys "$1"
  dialog_keys -k Return
  sleep 1.5
}

launch "" "$T/src.png"
export_to "$T/out/wall.png"
check "wall-left.png written (EXP-1)" yes "$([ -f "$T/out/wall-left.png" ] && echo yes)"
check "wall-right.png written (EXP-1)" yes "$([ -f "$T/out/wall-right.png" ] && echo yes)"
check "nothing else written (EXP-1)" "wall-left.png wall-right.png" "$(ls "$T/out" | tr '\n' ' ' | sed 's/ $//')"
check "left size (EXP-2)" "2560x1440" "$(magick identify -format '%wx%h' "$T/out/wall-left.png")"
check "right size (EXP-2)" "2560x1440" "$(magick identify -format '%wx%h' "$T/out/wall-right.png")"
check "PNG, 8 bits (EXP-2)" "PNG 8" "$(magick identify -format '%m %z' "$T/out/wall-left.png")"
magick "$T/out/wall-left.png" "$T/out/wall-right.png" +append "$T/joined.png"
check "joined halves equal the source, pixel for pixel (EXP-2)" 0 "$(magick compare -metric AE "$T/src.png" "$T/joined.png" null: 2>&1 | cut -d" " -f1)"

cleanup; sleep 0.5
launch "" "$T/src.png"
export_to "$T/locked/wall.png"
shot "$OUT/error.png"
check "an alert is open (EXP-3)" 2 "$(all_wins | jq length)"
check "nothing written into the read-only directory" "" "$(ls "$T/locked")"

echo "screenshots in $OUT"
[ "$FAILS" = 0 ]
