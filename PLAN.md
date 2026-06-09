# wall-split build plan

## Context

The repo currently contains only `AGENTS.md` (the spec, updated to Python + GTK 4 / PyGObject), a stale Swift `.gitignore`, and a deleted `flake.nix`. No source code exists. Goal: stand up a working GTK 4 app that loads a wallpaper via drag-and-drop, lets the user choose an aspect-ratio pairing for a non-destructive vertical split, previews it, and exports two PNGs.

## Design decisions

- **Image I/O:** `GdkPixbuf` only — no Pillow dependency. 8-bit per channel is acceptable.
- **Cut control:** Pairing dropdown + slider. Dropdown lists pairings that fit the loaded image; selecting one snaps the cut. Slider nudges off-snap; dropdown then reads "Custom".
- **Export:** Single `GtkFileDialog` for save; writes `<basename>-left.png` and `<basename>-right.png` (dashes).
- **Nix:** Restore `flake.nix` with a dev shell first; `nix develop` is the canonical entry point.

## File layout

```
wall-split/
  flake.nix                 # dev shell (step 1)
  .envrc                    # `use flake` (if direnv already wired — .direnv/ exists)
  pyproject.toml            # minimal, declares package + entry point
  .gitignore                # replace Swift entries with Python ones
  src/wall_split/
    __init__.py
    __main__.py             # `python -m wall_split` entry
    app.py                  # Gtk.Application subclass, window assembly
    split.py                # pure split math (no GTK imports) — easy to unit-test
    pairings.py             # common ratios + pairing generator
    dnd.py                  # GtkDropTarget setup, MIME filtering
    preview.py              # GtkDrawingArea + Cairo cut-line overlay
    export.py               # GtkFileDialog flow + pixbuf save
  tests/
    test_split.py
    test_pairings.py
```

## Step-by-step

### 1. `flake.nix` dev shell

Create `flake.nix` with `nixpkgs-unstable` input and a `devShells.default` exposing:

- `python3` with `pygobject3`
- `gtk4`, `glib`, `gobject-introspection`
- `pkg-config`, `gdk-pixbuf`
- (no libadwaita — spec forbids it)

Use `mkShell` with `nativeBuildInputs` for the C tooling and `buildInputs` for GTK; export `GI_TYPELIB_PATH` so `gi.repository` finds Gtk 4. Verify with `nix develop -c python -c "import gi; gi.require_version('Gtk','4.0'); from gi.repository import Gtk; print(Gtk._version)"`.

### 2. `.gitignore` and `pyproject.toml`

Replace Swift entries (`.build/`, `.swiftpm/`, `Package.resolved`) with Python ones (`__pycache__/`, `*.pyc`, `.pytest_cache/`, `dist/`, `*.egg-info/`). Keep `.direnv/` and `result`. Minimal `pyproject.toml` with `[project]` metadata and `[project.scripts] wall-split = "wall_split.app:main"`.

### 3. `split.py` — pure math (write tests alongside)

Functions, no GTK imports:

- `cut_x_for_left_ratio(W, H, left_ratio) -> int` → `round(H * left_ratio)`, clamped to `[0, W]`.
- `right_ratio_for_cut(W, H, x) -> float` → `(W - x) / H`.
- `snap_to_ratio(x, W, H, ratio, tolerance=0.02) -> int | None` — return snapped `x` if within tolerance, else `None`. Spec says ±2%.
- `split_sizes(W, H, x) -> ((x, H), (W - x, H))`.

Unit-tested in `tests/test_split.py` against the load-bearing rule: every source pixel ends up in exactly one output, no rescaling.

### 4. `pairings.py` — pairing generator

- `COMMON_RATIOS: list[tuple[str, float]]` — `[("16:9", 16/9), ("21:9", 21/9), ("16:10", 16/10), ("4:3", 4/3), ("5:4", 5/4), ("32:9", 32/9), ("1:1", 1.0)]`.
- `viable_pairings(W, H, tolerance=0.02) -> list[Pairing]` — iterate `COMMON_RATIOS` as the left side, compute the implied right ratio, return only those whose right ratio also matches a common ratio within tolerance. Each `Pairing` carries `(left_label, right_label, cut_x)`.
- Special-case "preferred default": if 16:9 + 16:9 is viable (source ≈ 32:9), it leads the list and is the initial selection.

Unit-tested in `tests/test_pairings.py` with several source ratios (32:9, 16:9, 21:9, 4:3).

### 5. `app.py` + `__main__.py` — window assembly

- `Gtk.Application` with `application_id = "lol.weston.wall-split"`.
- Single `Gtk.ApplicationWindow`. Vertical `Gtk.Box`:
  1. Header strip with file name + "Export…" button (plain `Gtk.HeaderBar`, no libadwaita).
  2. Preview area (`preview.py`) — fills available space.
  3. Controls row: `Gtk.DropDown` of pairings, `Gtk.Scale` for the cut position, labels showing live left/right ratios in source pixels.
- Empty state: a centered drop-zone label until an image is loaded.
- `main()` entry point creates the app and calls `app.run(sys.argv)`.

### 6. `dnd.py` — drag-and-drop

`GtkDropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)`, connected to the window's content area. On `drop`:

- Pull the first `Gio.File`, query its content type, reject anything not `image/*` (visible cue: brief red border via CSS class on the drop area).
- On accept: load into a `GdkPixbuf.Pixbuf`, store on the app state, recompute viable pairings, populate the dropdown, draw the preview.

### 7. `preview.py` — preview + cut line

- `Gtk.DrawingArea` with a `set_draw_func`. On draw: scale the source pixbuf to fit (preserving aspect), then draw a 2 px vertical line at the scaled cut position. Mouse drag on the line is a stretch goal; the `Gtk.Scale` is the primary control for v1.
- Keep slider, dropdown, and cut state in sync via a single source of truth in `app.py` (`cut_x` in source pixels). Slider's `value-changed` → recompute pairing label (sets dropdown to "Custom" if no snap match). Dropdown's `notify::selected` → set `cut_x` from the pairing.

### 8. `export.py` — save flow

- "Export…" opens a single `Gtk.FileDialog.save()` prompting for a base file name + directory.
- After the user confirms, derive `<dir>/<base>-left.png` and `<dir>/<base>-right.png`.
- Crop using `pixbuf.new_subpixbuf(0, 0, x, H)` and `pixbuf.new_subpixbuf(x, 0, W - x, H)`; save both via `pixbuf.savev("png", [], [])`.
- Error handling: surface IO errors via a `Gtk.AlertDialog`.

### 9. Wire entry point

- `python -m wall_split` runs `app.main()`.
- `pyproject.toml` script `wall-split` does the same after `pip install -e .` inside the dev shell.

## Verification

End-to-end, inside `nix develop`:

1. `python -m pytest tests/` — split math + pairing generator pass.
2. `python -m wall_split` — window opens with empty drop zone.
3. Drag a 5120×1440 image (≈32:9): dropdown defaults to "16:9 + 16:9"; preview shows centered cut line.
4. Drag a 3840×1080 image (16:9, narrower): dropdown shows alternatives (e.g. "16:9 + 32:9" should *not* appear because right side is unviable; "4:3 + 16:9" might). Slider moves the cut; "Custom" appears in the dropdown when off-snap.
5. Drag a non-image file (`.txt`): rejected with visible cue, app state unchanged.
6. Export: pick `~/Pictures/wall`, confirm `wall-left.png` and `wall-right.png` appear, dimensions sum to source width, both `H` pixels tall, no rescaling artifacts (compare a column at the cut against the source).

## Out of scope (v1)

- Mouse drag on the cut line in preview.
- Non-PNG formats / higher bit depths (would require Pillow).
- Persisting recent pairings or last-used directory.
- libadwaita styling.
