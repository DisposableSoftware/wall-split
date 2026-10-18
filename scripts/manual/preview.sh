#! /usr/bin/env nix-shell
#! nix-shell -i bash -p wtype jq grim imagemagick
# Spec: WIN-5.
# Run from the repo root after `nix build`, with no Wall Split windows open. Loads a
# 5120×1440 image, blue on the left half and green on the right: a preview that fits the
# whole image shows as much blue as green, with the cut line on the boundary.
cd "$(dirname "$0")/../.." || exit 1
. scripts/manual/lib.sh
require_no_instance

T=$(mktemp -d); trap 'cleanup; rm -rf "$T"' EXIT
OUT=${OUT:-$T/shots}; mkdir -p "$OUT"
magick -size 2560x1440 xc:'#0000ff' -size 2560x1440 xc:'#00ff00' +append "$T/halves.png"

# share COLOUR: the fraction of the screenshot's pixels that are COLOUR.
share() { magick "$OUT/preview.png" -fuzz 3% -fill white -opaque "$1" -fill black +opaque white -format '%[fx:mean]' info:; }

launch "" "$T/halves.png"
shot "$OUT/preview.png"
blue=$(share '#0000ff'); green=$(share '#00ff00')
check "both halves are visible (WIN-5)" yes "$(awk -v b="$blue" -v g="$green" 'BEGIN { print (b > 0.1 && g > 0.1) ? "yes" : "no" }')"
check "the halves are the same size (WIN-5)" yes "$(awk -v b="$blue" -v g="$green" 'BEGIN { d = b - g; if (d < 0) d = -d; print (d / (b + g) < 0.03) ? "yes" : "no" }')"
echo "blue $blue, green $green"

echo "screenshots in $OUT"
[ "$FAILS" = 0 ]
