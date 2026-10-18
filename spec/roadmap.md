# Roadmap

The order of approved work: `planned` requirements, and `partial` ones with a known bug from `/bug`. Change it here when priorities change. `/implement` works through this file: the verification backlog first, then the requirements in the order listed.

1. `INT-3`, `INT-4`: package the app, so the manual scripts have a binary to launch.
2. `WIN-5`: scale the preview to fit.
3. `WIN-7`: slider in whole pixels, shown as a ratio, with a "Custom" dropdown entry.
4. `WIN-4`: a visible cue when a drop is rejected.
5. `WIN-1`: request GTK 4 explicitly.
6. `WIN-2`: the DisposableSoftware app ID.
7. `PROD-4`: load and save asynchronously.
8. `INT-2`: a plain `python -m wall_split` entry point.

## Verification backlog

Built requirements that are not fully verified. Clear these before starting new planned work. The manual checks need `INT-3` first; drag-and-drop checks need a real Hyprland session, because the headless runner can't drag a file.

- `SPLIT-4`: unit tests for the ±2% boundary and for a source with no pairings.
- `SPLIT-6`: default cut when nothing fits.
- `WIN-3`, `WIN-6`, `WIN-8`: load, dropdown and labels.
- `EXP-1`, `EXP-2`, `EXP-3`: export naming, pixels and errors.
