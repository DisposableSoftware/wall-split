# Export

## Requirements

| ID | Requirement | Status | Verified by |
|----|-------------|--------|-------------|
| `EXP-1` | "Export..." opens one save dialog every time, suggesting `wallpaper.png`. The chosen name without its extension is the base, and the app writes `<dir>/<base>-left.png` and `<dir>/<base>-right.png`. | done | `scripts/manual/export.sh` (headless: saving as `wall.png` writes exactly `wall-left.png` and `wall-right.png`) |
| `EXP-2` | Both outputs are PNG with 8 bits per channel, keep the source's alpha channel if it has one, and hold the source's pixels unchanged (`SPLIT-1`). | done | `scripts/manual/export.sh` (headless: both 2560×1440 8-bit PNGs, and joined they equal the 8-bit source pixel for pixel) |
| `EXP-3` | If writing either file fails, an alert dialog shows the error. | partial: no alert appears; `export._show_error` calls `Gtk.AlertDialog.new`, which PyGObject doesn't have, so it raises `AttributeError` | `scripts/manual/export.sh` (headless: export into a read-only directory; fails now) |
