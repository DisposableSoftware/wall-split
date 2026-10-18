# Window

## Requirements

| ID | Requirement | Status | Verified by |
|----|-------------|--------|-------------|
| `WIN-1` | Starting the app opens one GTK 4 window titled "Wall Split", 960×640 logical px by default. Its header bar shows "No image loaded" and a disabled "Export..." button, and the body shows "Drag and drop an image here" centred. | done | `scripts/manual/smoke.sh` (headless: title, 960×640, no PyGIWarning; screenshot) |
| `WIN-2` | The window has the Wayland app ID `io.github.DisposableSoftware.WallSplit`, so compositor window rules match it. | done | `scripts/manual/smoke.sh` (headless: `swaymsg` reports the app ID) |
| `WIN-3` | Dropping a file whose content is an image loads it: the header shows the file name, the preview replaces the hint, the pairings are recomputed (`SPLIT-4`), the cut moves to the default (`SPLIT-5`, `SPLIT-6`) and Export is enabled. | partial: the content type is guessed from the file name only; not verified | manual on Hyprland (drag from a file manager) |
| `WIN-4` | Dropping anything else (a non-image, or an image that fails to decode) is rejected with a visible cue, and the loaded image and cut stay as they were. | partial: rejected, but with no cue | manual on Hyprland |
| `WIN-5` | The preview shows the whole image scaled to fit the area with its aspect ratio kept, and a vertical line at the cut. | partial: the image is painted at native size, not scaled, so an image larger than the area is cropped and the line doesn't sit on the cut | manual (screenshot with a 5120×1440 image) |
| `WIN-6` | The pairing dropdown lists each pairing as "L + R" (e.g. "16:9 + 16:9"). Selecting one moves the cut to it and updates the slider, preview and size labels. | partial: built, not verified | manual |
| `WIN-7` | The slider moves the cut in whole source pixels over `[1, W−1]`, so neither output is empty, and shows its position as the left-side ratio. The slider, dropdown, preview and labels stay in sync: when the cut matches no pairing, the dropdown shows "Custom". | partial: the slider shows the raw pixel value with 4 decimals, and there is no "Custom" entry, so the dropdown keeps the last pairing | manual |
| `WIN-8` | Two labels show each side's size in pixels and its ratio to 2 decimals (e.g. "Left: 2560×1440 (1.78)"), updated as the cut moves. | partial: built, not verified | manual |
| `WIN-9` | `wall-split FILE` loads `FILE` as if it had been dropped on the window (`WIN-3`, `WIN-4`). If the app is already running, the file loads in its window. With several files, only the first is used. | done | `scripts/manual/smoke.sh` (headless: two files opened from the command line load into one window) |

## Implementation notes

- `GtkDropTarget` with `Gdk.FileList` and `Gdk.DragAction.COPY`, on the stack that holds the hint and the preview.
- The cut position `cut_x` in source pixels is the single source of truth in `app.py`. The dropdown and slider both write it.
- `WIN-7` widens the cut range of the original `AGENTS.md` (`[0, W]`) to `[1, W−1]`: a zero-width output can't be saved.
