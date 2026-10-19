#! /usr/bin/env nix-shell
#! nix-shell -i bash -p wtype jq grim imagemagick
# Spec: CROP-2, CROP-3, CROP-4, CROP-5, WIN-13.
# Run headless from the repo root after `nix build`, with no Wall Split windows open:
#   ./scripts/manual/headless.sh ./scripts/manual/crop.sh
# The monitor fields prefill to 3840×2160 and 2560×1440 (CROP-1), both 16:9. Loads a
# 6000×3000 image and switches to crop mode. The box is found in each screenshot from its
# white outline and handles, which anti-aliasing blurs by a few px, so the checks allow
# for that; the labels in the screenshots in $OUT give the exact numbers:
#   1-placed    the largest 32:9 box, centred: "Box: 6000×1688 at 0, 656", the rest dimmed,
#               the red cut line in the middle of the box
#   2-reshaped  right width typed as 3440: the box keeps its centre and shrinks to fit,
#               "Box: 6000×1440 at 0, 780", the cut at 16/9 ÷ (16/9 + 3440/1440) ≈ 43% across
#   3-resized   bottom-right corner dragged up and left: smaller, same top-left, same shape
#   4-moved     dragged from inside: the label's position follows the box
#   5-clamped   dragged far down and right: the box ends at 6000, 3000 (x + w, y + h)
#   6-smallest  top-left corner dragged past the opposite corner: "Box: 267×64", same corner
cd "$(dirname "$0")/../.." || exit 1
. scripts/manual/lib.sh
require_no_instance
[ -n "${HEADLESS:-}" ] || { echo "run this under scripts/manual/headless.sh" >&2; exit 2; }

T=$(mktemp -d); trap 'cleanup; rm -rf "$T"' EXIT
OUT=${OUT:-$T/shots}; mkdir -p "$OUT"
magick -size 6000x3000 plasma:fractal -depth 8 "$T/big.png"

# box FILE: "x y w h" of the crop box in logical px inside the window. The handles stick out
# HANDLE/2 = 4 px past the corners.
box() {
  local s; s=$(display_scale)
  magick "$1" -fill black +opaque white -format '%@' info: |
    awk -v s="$s" -F'[x+]' '{ printf "%d %d %d %d\n", $3 / s + 4, $4 / s + 4, $1 / s - 8, $2 / s - 8 }'
}
near() { awk -v a="$1" -v b="$2" -v t="${3:-2}" 'BEGIN { d = a - b; if (d < 0) d = -d; print (d <= t) ? "yes" : "no" }'; }

launch "" "$T/big.png"
pointer_start
# Ctrl+2 switches to crop mode (WIN-13); the right monitor's width field is clicked.
keys -M ctrl 2 -m ctrl
shot "$OUT/1-placed.png"
pointer_click 400 565
keys -M ctrl a -m ctrl
keys 3440
keys -k Return
shot "$OUT/2-reshaped.png"

read -r x y w h < <(box "$OUT/2-reshaped.png")
# The box is the image's full width here, so the image spans x .. x + w at 6000 source px.
scale=$(awk -v w="$w" 'BEGIN { print w / 6000 }')
img_x=$x; img_r=$((x + w)); img_b=$(awk -v y="$y" -v s="$scale" 'BEGIN { printf "%d", y - 780 * s + 3000 * s }')
ratio=$(awk -v w="$w" -v h="$h" 'BEGIN { print w / h }')

pointer_drag $((x + w)) $((y + h)) $((x + w - 300)) $((y + h - 40))
shot "$OUT/3-resized.png"
read -r x3 y3 w3 h3 < <(box "$OUT/3-resized.png")
check "corner resize keeps the top-left corner (CROP-4)" "yes yes" "$(near "$x3" "$x") $(near "$y3" "$y")"
check "corner resize shrinks the box (CROP-4)" yes "$([ "$w3" -lt "$w" ] && echo yes)"
check "corner resize keeps the shape (CROP-4)" yes "$(near "$(awk -v w="$w3" -v h="$h3" 'BEGIN { print w / h * 100 }')" "$(awk -v r="$ratio" 'BEGIN { print r * 100 }')" 4)"

pointer_drag $((x3 + w3 / 2)) $((y3 + h3 / 2)) $((x3 + w3 / 2 + 120)) $((y3 + h3 / 2 + 30))
shot "$OUT/4-moved.png"
read -r x4 y4 w4 h4 < <(box "$OUT/4-moved.png")
# The resized box touches the window's left edge, which clips its handles; measure the
# move and the size from the right edge and the height, which stay clear of it.
check "dragging inside moves the box (CROP-4)" "yes yes" "$(near $((x4 + w4)) $((x3 + w3 + 120))) $(near "$y4" $((y3 + 30)))"
check "moving keeps the size (CROP-4)" yes "$(near "$h4" "$h3")"

pointer_drag $((x4 + w4 / 2)) $((y4 + h4 / 2)) $((x4 + w4 / 2 + 2000)) $((y4 + h4 / 2 + 2000))
shot "$OUT/5-clamped.png"
read -r x5 y5 w5 h5 < <(box "$OUT/5-clamped.png")
check "the box stops at the image's right and bottom edges (CROP-4)" "yes yes" "$(near $((x5 + w5)) "$img_r" 4) $(near $((y5 + h5)) "$img_b" 4)"

pointer_drag "$x5" "$y5" $((x5 + w5 + 400)) $((y5 + h5 + 400))
shot "$OUT/6-smallest.png"
read -r x6 y6 w6 h6 < <(box "$OUT/6-smallest.png")
check "the box is never less than 64 source px tall (CROP-4)" yes "$(near "$h6" "$(awk -v s="$scale" 'BEGIN { printf "%d", 64 * s }')" 5)"
check "and keeps the opposite corner (CROP-4)" "yes yes" "$(near $((x6 + w6)) $((x5 + w5))) $(near $((y6 + h6)) $((y5 + h5)))"

echo "screenshots in $OUT"
[ "$FAILS" = 0 ]
