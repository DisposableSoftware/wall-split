# Roadmap

The order of approved work: `planned` requirements, and `partial` ones with a known bug from `/bug`. Change it here when priorities change. `/implement` works through this file: the verification backlog first, then the requirements in the order listed.

1. `CROP-2`, `CROP-3`: the box shape and its starting place (pure math, unit-tested first).
2. `WIN-10`: the mode switch (built; done once the box is drawn).
3. `CROP-1`: the monitor fields, prefilled from the connected monitors.
4. `CROP-4`, `CROP-5`: drawing, moving and resizing the box, and its label.
5. `CROP-6`: export in crop mode.


## Verification backlog

Built requirements that are not fully verified. Clear these before starting new planned work. The manual checks need `INT-3` and `WIN-9` first: the headless runner can't drag a file, so they load images from the command line. Only the drag itself needs a real Hyprland session.

None.

