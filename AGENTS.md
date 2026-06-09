# AGENTS.md

This file provides guidance to Agents when working with code in this repository.

## Project

`wall-split` is a GTK desktop app for splitting a single wallpaper image into two halves for a dual-monitor setup. The user drops an image onto the window, the app proposes output aspect-ratio pairings, and a slider adjusts where the vertical cut falls between left and right.

## Stack

- **Language:** Python 3.
- **UI:** GTK 4 via `PyGObject` (`gi.repository.Gtk`). No libadwaita. Plain GTK widgets only — keep it portable across desktops (Hyprland is the dev target but the app should not depend on GNOME).
- **Packaging on NixOS:** prefer a `flake.nix` with a dev shell that pulls in `python3` with `pygobject3`, `gtk4`, `glib`, and `pkg-config`. Build via `nix develop` rather than relying on system packages.

## Core behavior (load-bearing — read before changing split logic)

The split is **non-destructive on the whole image**: every source pixel ends up in exactly one of the two output images. The slider controls the **horizontal cut position**, not a crop.

Consequences:

- For a source image of width `W` and height `H`, a cut at column `x` produces a left image of size `x × H` and a right image of size `(W - x) × H`. Output is in **native pixels** — no rescaling.
- The "aspect ratio" controls are really controls over `x`. Picking left = 16:9 with `H` fixed means `x = round(H * 16 / 9)`; the right side's ratio is whatever `(W - x) / H` works out to.
- **Preferred default:** 16:9 + 16:9. This is only achievable when the source ratio is ≈ 32:9. Within a small tolerance (suggest ±2%) snap to exact 16:9/16:9.
- **When 16:9/16:9 isn't suitable** (source ratio too far off 32:9), present the set of pairings that fit the source: e.g. 16:9 + 21:9, 16:10 + 16:10, 4:3 + 16:9, etc. Generate this list by iterating common monitor ratios for the left side and reporting the implied right-side ratio; surface the pairings whose right side is also a common ratio (within tolerance).
- Slider range is `[0, W]` in source pixels but presented to the user as the left-side aspect ratio. Both representations must stay in sync.

## Export

- Save dialog per export — prompt for path and filename each time (one dialog per side, or one dialog that writes `*_left.png` / `*_right.png`; pick whichever feels less annoying after trying it).
- Output format: PNG by default. Preserve source bit depth where the toolkit allows.

## Drag-and-drop

GTK 4 uses `GtkDropTarget` with `GdkFileList` / `Gio.File` for file drops. The drop zone should accept image MIME types and reject everything else with a visible cue.

## Repo conventions

- Don't add comments that describe what code does. Only comment the *why* when it's non-obvious (e.g. a GTK quirk, a rounding choice in the split math).
- No libadwaita imports. If a widget only exists in libadwaita, write the plain-GTK equivalent.
- This repo lives outside `~/Developer/nix-config`; don't touch the NixOS config from here. App-level Nix lives in this repo's own `flake.nix`.
