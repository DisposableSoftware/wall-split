#! /usr/bin/env nix-shell
#! nix-shell -i bash -p wtype jq grim imagemagick
# Spec: WIN-6, WIN-7, WIN-8, SPLIT-6, WIN-3.
# Run from the repo root after `nix build`, with no Wall Split windows open. Loads a
# 5120×1440 image; check the screenshots in $OUT:
#   1-loaded  dropdown "16:9 + 16:9", slider "1.78", "Left: 2560×1440 (1.78)", "Right: 2560×1440 (1.78)"
#   2-pairing "5:4 + 21:9" picked in the dropdown: slider "1.25", "Left: 1800×1440 (1.25)",
#             "Right: 3320×1440 (2.31)", the line at about a third of the preview
#   3-custom  one pixel right: dropdown "Custom", "Left: 1801×1440", "Right: 3319×1440"
#   4-back    one pixel left again: dropdown "5:4 + 21:9", 1800 and 3320
#   5-square  a 1001×1000 image opened from the command line, which fits no pairing: the
#             dropdown "Custom", "Left: 500×1000", "Right: 501×1000"
cd "$(dirname "$0")/../.." || exit 1
. scripts/manual/lib.sh
require_no_instance

T=$(mktemp -d); trap 'cleanup; rm -rf "$T"' EXIT
OUT=${OUT:-$T/shots}; mkdir -p "$OUT"
magick -size 5120x1440 gradient:red-blue "$T/wide.png"
magick -size 1001x1000 gradient:green-yellow "$T/square.png"

launch "" "$T/wide.png"
shot "$OUT/1-loaded.png"
# Focus order: Split, Crop and Export come first; the fifth Tab reaches the dropdown.
keys -k Tab -k Tab -k Tab -k Tab -k Tab
keys -k space
keys -k Down
keys -k Return
shot "$OUT/2-pairing.png"
keys -k Tab
keys -k Right
shot "$OUT/3-custom.png"
keys -k Left
shot "$OUT/4-back.png"
"$BIN" "$T/square.png" >/dev/null 2>&1
sleep 1
shot "$OUT/5-square.png"

echo "screenshots in $OUT"
[ "$FAILS" = 0 ]
