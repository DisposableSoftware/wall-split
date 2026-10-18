# Roadmap

The order of approved work: `planned` requirements, and `partial` ones with a known bug from `/bug`. Change it here when priorities change. `/implement` works through this file: the verification backlog first, then the requirements in the order listed.

1. `INT-3`, `INT-4`: package the app, so the manual scripts have a binary to launch.
2. `WIN-9`: open a file from the command line, so headless checks can load an image.
3. `WIN-5`: scale the preview to fit.
4. `WIN-7`: slider in whole pixels, shown as a ratio, with a "Custom" dropdown entry.
5. `WIN-4`: a visible cue when a drop is rejected.
6. `WIN-1`: request GTK 4 explicitly.
7. `WIN-2`: the DisposableSoftware app ID.
8. `PROD-4`: load and save asynchronously.
9. `INT-2`: a plain `python -m wall_split` entry point.

## Verification backlog

Built requirements that are not fully verified. Clear these before starting new planned work. The manual checks need `INT-3` and `WIN-9` first: the headless runner can't drag a file, so they load images from the command line. Only the drag itself needs a real Hyprland session.

- `SPLIT-6`: default cut when nothing fits.
- `WIN-3`, `WIN-6`, `WIN-8`: load, dropdown and labels.
- `EXP-1`, `EXP-2`, `EXP-3`: export naming, pixels and errors.
