#! /usr/bin/env nix-shell
#! nix-shell -i bash -p wtype jq grim imagemagick
# Spec: CROP-2, CROP-3, CROP-5.
# Run from the repo root after `nix build`, with no Wall Split windows open. Headless, the
# monitor fields prefill to 3840×2160 and 2560×1440 (CROP-1), both 16:9. Loads a 6000×3000
# image and switches to crop mode; check the screenshots in $OUT:
#   1-placed    the largest 32:9 box, centred: "Box: 6000×1688 at 0, 656", the rest dimmed,
#               the red cut line in the middle of the box
#   2-reshaped  right width typed as 3440: the box keeps its centre and shrinks to fit,
#               "Box: 6000×1440 at 0, 780", the cut at 16/9 ÷ (16/9 + 3440/1440) ≈ 43% across
cd "$(dirname "$0")/../.." || exit 1
. scripts/manual/lib.sh
require_no_instance

T=$(mktemp -d); trap 'cleanup; rm -rf "$T"' EXIT
OUT=${OUT:-$T/shots}; mkdir -p "$OUT"
magick -size 6000x3000 plasma:fractal -depth 8 "$T/big.png"

launch "" "$T/big.png"
# Focus order: Split, Crop, Export, then in crop mode the four monitor fields.
keys -k Tab -k Tab -k Tab
keys -k space
shot "$OUT/1-placed.png"
keys -k Tab -k Tab -k Tab -k Tab
keys -M ctrl a -m ctrl
keys 3440
keys -k Return
shot "$OUT/2-reshaped.png"

echo "screenshots in $OUT"
[ "$FAILS" = 0 ]
