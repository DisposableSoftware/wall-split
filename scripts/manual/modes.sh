#! /usr/bin/env nix-shell
#! nix-shell -i bash -p wtype jq grim imagemagick
# Spec: WIN-10, WIN-11, WIN-13, CROP-1.
# Run from the repo root after `nix build`, with no Wall Split windows open. Loads
# tests/assets/wide.png and switches modes with Ctrl+2 and Ctrl+1 (WIN-13); check the screenshots in $OUT:
#   1-split  "Split" pressed; dropdown "16:9 + 16:9", slider, labels, the red cut line
#   2-crop   "Crop" pressed; the Left and Right width × height fields (prefilled: 3840×2160
#            from the headless output, 2560×1440 for the missing second monitor) and "Box:" label
#            instead of the split controls, and no cut line
#   3-split  back in split mode with the same dropdown, slider and labels as 1-split
cd "$(dirname "$0")/../.." || exit 1
. scripts/manual/lib.sh
require_no_instance

T=$(mktemp -d); trap 'cleanup; rm -rf "$T"' EXIT
OUT=${OUT:-$T/shots}; mkdir -p "$OUT"

launch "" "$PWD/tests/assets/wide.png"
shot "$OUT/1-split.png"
keys -M ctrl 2 -m ctrl
shot "$OUT/2-crop.png"
keys -M ctrl 1 -m ctrl
shot "$OUT/3-split.png"
check "same split view after a round trip (WIN-10)" yes "$(magick compare -metric AE "$OUT/1-split.png" "$OUT/3-split.png" null: 2>&1 | awk '{ print ($1 < 2000) ? "yes" : "no" }')"
check "crop mode looks different" yes "$(magick compare -metric AE "$OUT/1-split.png" "$OUT/2-crop.png" null: 2>&1 | awk '{ print ($1 > 2000) ? "yes" : "no" }')"

echo "screenshots in $OUT"
[ "$FAILS" = 0 ]
