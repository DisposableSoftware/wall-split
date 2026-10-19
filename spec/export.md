# Export

## Requirements

| ID | Requirement | Status | Verified by |
|----|-------------|--------|-------------|
| `EXP-1` | "Save..." (`WIN-11`) opens one save dialog every time, suggesting `wallpaper.png`. The chosen name without its extension is the base, and the app writes `<dir>/<base>-left.png` and `<dir>/<base>-right.png`. | done | `scripts/manual/export.sh` (headless: saving as `wall.png` writes exactly `wall-left.png` and `wall-right.png`) |
| `EXP-2` | Both outputs are PNG with 8 bits per channel and keep the source's alpha channel if it has one. In split mode they hold the source's pixels unchanged (`SPLIT-1`); in crop mode they are resampled (`CROP-6`). | done | `scripts/manual/export.sh` (headless: both 2560×1440 8-bit PNGs, and joined they equal the 8-bit source pixel for pixel) |
| `EXP-3` | If writing either file fails, an alert dialog shows the error. | done | `scripts/manual/export.sh` (headless: export into a read-only directory and an alert opens with the "Permission denied" error; failed before the fix) |
| `EXP-4` | The error alert (`EXP-3`) follows the guide's copy: a message `Could not save “<name>”` with the system's error text as the detail, sentence case, no exclamation marks. Source: `docs/interaction.md` (Copy). | planned | `scripts/manual/export.sh` (read-only directory: message and detail) |

## Implementation notes

- Build the alert with `Gtk.AlertDialog(message=...)`. `gtk_alert_dialog_new` takes a printf-style format and varargs, which GObject introspection can't describe, so PyGObject has no `Gtk.AlertDialog.new` (`EXP-3`). The same goes for any other variadic GTK constructor.
