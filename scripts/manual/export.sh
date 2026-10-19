#! /usr/bin/env nix-shell
#! nix-shell -i bash -p wtype jq grim imagemagick
# Spec: EXP-1, EXP-2, EXP-3, PROD-4, CROP-6.
# Run from the repo root after `nix build`, with no Wall Split windows open. Loads a
# 5120×1440 image, exports it as wall.png through the save dialog, and compares the two
# outputs with the source. Then exports into a read-only directory and screenshots the
# error alert. Last, in crop mode (headless: the monitors prefill to 3840×2160 and
# 2560×1440), exports a box from an image whose bands outside the box must not appear.
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

# Crop mode (CROP-6): red | blue split at x = 3000 between a green top band and a yellow
# bottom band. The 32:9 box covers rows 656 to 2344, so the left file is all red at the left
# monitor's size and the right all blue at the right's.
magick \( -size 6000x600 xc:"#00ff00" \) \( -size 3000x1800 xc:"#ff0000" -size 3000x1800 xc:"#0000ff" +append \) \( -size 6000x600 xc:"#ffff00" \) -append -depth 8 "$T/bands.png"
mkdir -p "$T/crop"
cleanup; sleep 0.5
launch "" "$T/bands.png"
keys -k Tab -k Tab -k Tab
keys -k space
keys -k Tab
keys -k space
sleep 1
check "the save dialog opened in crop mode" 2 "$(all_wins | jq length)"
dialog_keys -M ctrl a -m ctrl
dialog_keys "$T/crop/wall.png"
dialog_keys -k Return
sleep 2
check "left is the left monitor's size (CROP-6)" "3840x2160" "$(magick identify -format '%wx%h' "$T/crop/wall-left.png")"
check "right is the right monitor's size (CROP-6)" "2560x1440" "$(magick identify -format '%wx%h' "$T/crop/wall-right.png")"
not_colour() { magick "$1" -fuzz 10% -fill black -opaque "$2" -fill white +opaque black -format '%[fx:mean*w*h]' info:; }
check "left is all red, nothing from outside the box (CROP-6)" 0 "$(not_colour "$T/crop/wall-left.png" "#ff0000")"
check "right is all blue, nothing from outside the box (CROP-6)" 0 "$(not_colour "$T/crop/wall-right.png" "#0000ff")"

echo "screenshots in $OUT"
[ "$FAILS" = 0 ]
