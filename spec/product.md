# Product

Wall Split turns one wallpaper image into two images for a dual-monitor setup. The user drops an image onto the window and works in one of two modes: in split mode they pick an aspect-ratio pairing or move a slider to place a vertical cut through the whole image (`SPLIT`); in crop mode they drag a box, fixed to the two monitors' combined shape, over part of the image (`CROP`). Either way they save the two halves. Display name **Wall Split**, binary `wall-split`, app ID `io.github.DisposableSoftware.WallSplit` (`WIN-2`).

## Requirements

| ID | Requirement | Status |
|----|-------------|--------|
| `PROD-1` | Lightweight and minimal: plain GTK 4 widgets, no libadwaita, a short dependency list (PyGObject and GdkPixbuf; no Pillow). | done (ongoing constraint) |
| `PROD-2` | Portable across desktops: no dependency on GNOME services. Hyprland is the primary target. | done (ongoing constraint) |
| `PROD-3` | Simple toolchain: Python and pytest inside a Nix devshell, nothing else. | done |
| `PROD-4` | The main loop never blocks on file I/O: loading the dropped image and writing the PNGs are asynchronous. | done (ongoing constraint; loading uses `Gio.File.read_async` and `Pixbuf.new_from_stream_async`, saving `replace_async` and `save_to_streamv_async`; checked by review and the manual scripts, not by timing) |
| `PROD-5` | The public README follows the style guide's shape (`docs/readme.md`): centred icon and name, a tagline in the guide's form, the vibe-coded `[!WARNING]` callout, screenshots (including the shortcut overlay and one light flavor), and the sections Features, Install, Usage, Keyboard (a key table), Configuration, Development, Credits (Catppuccin, with both links) and License. | planned |

## Style guide

Wall Split follows the DisposableSoftware style guide (https://github.com/DisposableSoftware/style-guide), which describes the look and feel the apps share: minimal chrome, Catppuccin colours, keyboard-first, plain short text. The guide is a reference, not part of this spec. Where it and this spec disagree, this spec wins. The palette is Catppuccin, by the Catppuccin community (https://catppuccin.com), not ours. The rows that bring the app in line with the guide cite the page they come from.

## Non-goals

- No libadwaita. It fights custom theming and transparency.
- No more than two outputs.
- No header bar, title bar or status bar. The user runs Hyprland barless, as Junk Drawer and Downer do.

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
