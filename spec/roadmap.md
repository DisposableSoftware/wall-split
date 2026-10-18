# Roadmap

The order of approved work: `planned` requirements, and `partial` ones with a known bug from `/bug`. Change it here when priorities change. `/implement` works through this file: the verification backlog first, then the requirements in the order listed.

Nothing is planned.


## Verification backlog

Built requirements that are not fully verified. Clear these before starting new planned work. The manual checks need `INT-3` and `WIN-9` first: the headless runner can't drag a file, so they load images from the command line. Only the drag itself needs a real Hyprland session.

- `WIN-3`: drags are refused (see the row); needs `/bug`, then drag an image onto the window on Hyprland.
- `WIN-4`: drag a text file onto the window on Hyprland and see the red border.
- `EXP-3`: the error alert never appears (see the row); needs `/bug`.
