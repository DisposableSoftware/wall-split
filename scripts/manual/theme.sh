#! /usr/bin/env nix-shell
#! nix-shell -i bash -p wtype jq grim imagemagick
# Spec: LOOK-4, LOOK-5, LOOK-6, LOOK-10, CONF-4, CONF-8.
# Run headless after `nix build`: ./scripts/manual/headless.sh ./scripts/manual/theme.sh
# Starts the app with a temp XDG_CONFIG_HOME per flavor and takes split and crop mode
# screenshots into $OUT. Checks the first run creates a commented-out config.ini.
cd "$(dirname "$0")/../.." || exit 1
. scripts/manual/lib.sh
require_no_instance

T=$(mktemp -d); trap 'cleanup; rm -rf "$T"' EXIT
OUT=${OUT:-$T/shots}; mkdir -p "$OUT"
magick -size 5120x1440 plasma:fractal "$T/wide.png"

launch "$T/first" "$T/wide.png"
CFG=$T/first/wall-split/config.ini
check "first run creates config.ini (CONF-8)" yes "$([ -f "$CFG" ] && echo yes || echo no)"
check "every setting commented out (CONF-8)" 0 "$(grep -cE '^[a-z]' "$CFG")"
check "a setting is listed (CONF-8)" 1 "$(grep -c '^# flavor = mocha' "$CFG")"
cleanup; PID=; sleep 0.5

for flavor in mocha latte; do
  mkdir -p "$T/$flavor/wall-split"
  printf '[appearance]\nflavor = %s\n' "$flavor" > "$T/$flavor/wall-split/config.ini"
  launch "$T/$flavor" "$T/wide.png"
  sleep 0.5
  shot "$OUT/$flavor-split.png"
  keys -M ctrl 2 -m ctrl
  shot "$OUT/$flavor-crop.png"
  cleanup; PID=; sleep 0.5
done
mkdir -p "$T/empty/wall-split"
launch "$T/mocha"
shot "$OUT/mocha-empty.png"

echo "screenshots in $OUT"
[ "$FAILS" = 0 ]
