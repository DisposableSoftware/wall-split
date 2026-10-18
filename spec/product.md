# Product

Wall Split splits one wallpaper image into two images for a dual-monitor setup. The user drops an image onto the window, picks an aspect-ratio pairing or moves a slider to place a vertical cut, and exports the two halves. Display name **Wall Split**, binary `wall-split`, app ID `io.github.DisposableSoftware.WallSplit` (`WIN-2`).

## Requirements

| ID | Requirement | Status |
|----|-------------|--------|
| `PROD-1` | Lightweight and minimal: plain GTK 4 widgets, no libadwaita, a short dependency list (PyGObject and GdkPixbuf; no Pillow). | done (ongoing constraint) |
| `PROD-2` | Portable across desktops: no dependency on GNOME services. Hyprland is the primary target. | done (ongoing constraint) |
| `PROD-3` | Simple toolchain: Python and pytest inside a Nix devshell, nothing else. | done |
| `PROD-4` | The main loop never blocks on file I/O: loading the dropped image and writing the PNGs are asynchronous. | partial: `dnd.py` loads with `Pixbuf.new_from_file` and `export.py` saves with `savev`, both synchronously on the main loop |

## Non-goals

- No libadwaita. It fights custom theming and transparency.
- No rescaling or cropping: the outputs together hold every source pixel (`SPLIT-1`).
- No more than two outputs.

## Out of scope for now

Not rejected, just not planned. Use `/feature` to change that.

- Dragging the cut line in the preview with the mouse.
- Output formats other than PNG, and more than 8 bits per channel (GdkPixbuf can't; it would need another library).
- Remembering the last export directory or pairing.

## Stack constraints

- Python 3.11 or later with PyGObject. GTK 4 is requested explicitly (`gi.require_version("Gtk", "4.0")`) before any `gi.repository` import.
- GdkPixbuf for image I/O.
- Use GIO/GLib for anything they provide (MIME, files, paths) rather than reimplementing it or adding a package.
- Ask before adding a dependency.
