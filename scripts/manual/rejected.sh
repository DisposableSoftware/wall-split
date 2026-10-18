#! /usr/bin/env nix-shell
#! nix-shell -i bash -p wtype jq grim imagemagick
# Spec: WIN-3, WIN-4, WIN-9.
# Run from the repo root after `nix build`, with no Wall Split windows open. Loads an
# image, then opens a text file and a broken PNG from the command line: each one flashes
# a red border on the preview, and the loaded image and cut stay as they were. The type
# comes from the content, not the name: text called fake.png is rejected, and a PNG
# called picture.txt loads.
cd "$(dirname "$0")/../.." || exit 1
. scripts/manual/lib.sh
require_no_instance

T=$(mktemp -d); trap 'cleanup; rm -rf "$T"' EXIT
OUT=${OUT:-$T/shots}; mkdir -p "$OUT"
magick -size 2560x1440 xc:'#0000ff' -size 2560x1440 xc:'#00ff00' +append "$T/halves.png"
echo "not an image" > "$T/notes.txt"
head -c 4096 /dev/urandom > "$T/broken.png"
echo "not an image either" > "$T/fake.png"
magick -size 2000x1000 xc:"#ff00ff" "png:$T/picture.txt"

# share SHOT COLOUR: the fraction of the screenshot's pixels that are COLOUR.
share() { magick "$OUT/$1.png" -fuzz 3% -fill white -opaque "$2" -fill black +opaque white -format '%[fx:mean]' info:; }
some() { awk -v v="$1" 'BEGIN { print (v > 0) ? "yes" : "no" }'; }

launch "" "$T/halves.png"
shot "$OUT/loaded.png"
before=$(share loaded '#0000ff')
check "no border at first" no "$(some "$(share loaded '#e01b24')")"

for f in notes.txt broken.png fake.png; do
  "$BIN" "$T/$f" >/dev/null 2>&1
  sleep 0.3
  shot "$OUT/$f.png"
  check "$f: red border (WIN-4)" yes "$(some "$(share "$f" '#e01b24')")"
done

sleep 2
shot "$OUT/after.png"
check "the border goes away" no "$(some "$(share after '#e01b24')")"
# The border covers some of the image, so compare once it has gone.
check "image and cut unchanged (WIN-4)" "$before $(share loaded "#00ff00")" "$(share after "#0000ff") $(share after "#00ff00")"

"$BIN" "$T/picture.txt" >/dev/null 2>&1
sleep 1
shot "$OUT/picture.png"
check "a PNG named .txt loads (WIN-3)" yes "$(some "$(share picture "#ff00ff")")"
check "no border for it" no "$(some "$(share picture "#e01b24")")"

echo "screenshots in $OUT"
[ "$FAILS" = 0 ]
