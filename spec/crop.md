# Crop

Crop mode cuts the two wallpapers from a part of the image. A box shaped like the two monitors side by side is placed over the image, and each half of the box becomes one wallpaper at its monitor's resolution. Pixels outside the box are not used, unlike split mode (`SPLIT-1`).

## Requirements

| ID | Requirement | Status | Verified by |
|----|-------------|--------|-------------|
| `CROP-1` | In crop mode, the controls row shows the left and right monitor sizes as editable width × height fields in pixels (1–16384 each). They are prefilled from the connected monitors: the two leftmost by position, left to right, at their size in device pixels (logical size × scale). A missing monitor (fewer than two connected) is prefilled with 2560×1440. | planned | `tests/test_crop.py` (ordering and defaults from a list of monitors); headless: the 3840×2160 output at scale 2 prefills the left fields with 3840×2160 and the right with 2560×1440 |
| `CROP-2` | The box has the shape of the two monitors side by side at equal height: its width over its height is `Lw/Lh + Rw/Rh`, and the cut inside it falls at `(Lw/Lh) / (Lw/Lh + Rw/Rh)` of its width. Changing a monitor size reshapes the box around its centre and keeps it inside the image. | planned | `tests/test_crop.py` |
| `CROP-3` | Loading an image while in crop mode, or switching to crop mode with an image loaded, places the largest box of that shape that fits in the image, centred. | planned | `tests/test_crop.py`; headless screenshot |
| `CROP-4` | The preview draws the box over the image, dims everything outside it, and draws a vertical line at the cut inside it. Dragging inside the box moves it; dragging a corner resizes it with the opposite corner fixed and the shape kept. The box always stays inside the image and is never less than 64 source pixels tall. | planned | `tests/test_crop.py` (move, corner resize, clamping, minimum size); headless drags with the sway cursor and screenshots |
| `CROP-5` | A label shows the box's position and size in source pixels (e.g. "Box: 4800×1350 at 160, 45"), updated as it moves. | planned | headless screenshot |
| `CROP-6` | In crop mode, Export writes `<base>-left.png` and `<base>-right.png` (`EXP-1`): the box's left and right parts, each resampled to exactly its monitor's size. | planned | `scripts/manual/export.sh` (crop mode: output sizes equal the monitor fields, and the colours of a test image's regions land in the right file) |

## Implementation notes

- Monitor sizes come from `Gdk.Display.get_monitors()`: `get_geometry()` is in logical pixels, so multiply by `get_scale()` and round. This works on Hyprland and other desktops alike (`PROD-2`); `hyprctl` is not needed.
- Keep the box in source pixels as floats while dragging and round only for export, so slow drags at small preview scales still move it.
- Resample with `GdkPixbuf.InterpType.HYPER` when shrinking and `BILINEAR` when enlarging.
