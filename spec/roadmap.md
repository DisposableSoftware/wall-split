# Roadmap

The order of approved work: `planned` requirements, and `partial` ones with a known bug from `/bug`. Change it here when priorities change. `/implement` works through this file: the verification backlog first, then the requirements in the order listed.

The rows below bring the app in line with the DisposableSoftware style guide (`product.md`). Keys come first because the overlay, the man page and the example file all read the same table.

1. `CONF-10`: the keys table and `data/keybindings.example.ini`, with the spec test.
2. `CONF-9`: `keybindings.ini` read over the defaults, and its first-run file.
3. `WIN-14`: the `?` shortcut overlay.
4. `INT-7`: `--help` and the man page.
5. `CONF-11`: `[window] width` and `height`.
6. `EXP-4`: error alert copy.
7. `PROD-5`: README shape, last, so its Keyboard table and screenshots match the finished app.

## Awaiting a decision

Not ready for `/implement`. Settle with the user first.

- `LOOK-11`: the guide wants themed dialogs, but `Gtk.AlertDialog` and `Gtk.FileDialog` can't take the window class (a known gap in the guide). The row proposes a small themed window for the error alert and keeps the GTK file dialog. Ask whether to do that or to keep `AlertDialog` and record the exception.


## Verification backlog

Built requirements that are not fully verified. Clear these before starting new planned work. The manual checks need `INT-3` and `WIN-9` first: the headless runner can't drag a file, so they load images from the command line. Only the drag itself needs a real Hyprland session.

- `LOOK-6` (partial): check the dropdown popover list and the slider on latte in a screenshot.
- `LOOK-10` (partial): check `flavor = gtk` with a real GTK theme.
