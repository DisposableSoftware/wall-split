#! /usr/bin/env nix-shell
#! nix-shell -i bash -p wtype jq grim imagemagick oxipng
# Retakes docs/screenshots/split.png and crop.png (README), headless, default flavor.
# Run from the repo root after `nix build`, with no Wall Split windows open:
#   ./scripts/manual/headless.sh ./scripts/screenshots.sh
# Uses a generated wallpaper and an empty temp config, so no personal files or settings
# show. The window opens at 960x640 logical px; the output is scale 2 (1920x1280 shots).
cd "$(dirname "$0")/.." || exit 1
. scripts/manual/lib.sh
require_no_instance
[ -n "${HEADLESS:-}" ] || { echo "run this under scripts/manual/headless.sh" >&2; exit 2; }

T=$(mktemp -d); trap 'cleanup; rm -rf "$T"' EXIT
OUT=${OUT:-docs/screenshots}; mkdir -p "$OUT"
mkdir -p "$T/config"
magick -seed 11 -size 5120x1440 plasma:fractal -blur 0x20 -modulate 85,85,100 -depth 8 "$T/wall.png"

launch "$T/config" "$T/wall.png"
pointer_start
sleep 0.5
shot "$T/split.png"
keys -M ctrl 2 -m ctrl
# Shrink the box from its bottom-right handle, then move it, so the dimmed margin shows.
pointer_drag 957 367 770 315
pointer_drag 300 200 360 215
shot "$T/crop.png"

for n in split crop; do
  magick "$T/$n.png" -strip "$T/$n-s.png"
  oxipng -q -o 4 --strip all --out "$OUT/$n.png" "$T/$n-s.png"
done
ls -l "$OUT"/split.png "$OUT"/crop.png
