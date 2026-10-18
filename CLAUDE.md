# Wall Split

Splits one wallpaper into two images for a dual-monitor setup. Display name **Wall Split**, binary `wall-split`, app ID `io.github.DisposableSoftware.WallSplit`.

**What the app does is defined in [`spec/`](spec/README.md).** This file covers how to work on it. Read `spec/split.md` before changing the split logic: the split is non-destructive, and the controls move a cut, never a crop.

Unlike the other DisposableSoftware GTK apps, this one is Python and PyGObject, not Rust. The workflow is the same as `gtk-template`'s; the tooling is the Python equivalent.

## Spec-first workflow (mandatory)

Every change follows these steps, in order. Three skills run them. `/feature` (`.claude/skills/feature/`) turns a request into spec rows, and `/bug` (`.claude/skills/bug/`) reproduces a bug and finds the spec gap that let it happen. Both end by asking the user to **approve and implement** or **approve the spec only**, and neither writes code itself. `/implement` (`.claude/skills/implement/`) builds what is approved: it works through `spec/roadmap.md`, the verification backlog first and then the listed rows in order, with one commit per requirement.

1. **Spec.** Before touching code, update the relevant `spec/*.md`.
   - **New behaviour or a changed requirement:** add or edit a requirement row. A new row gets the next free ID in its prefix, with status `planned`. If the request is unclear, settle the wording with the user before coding.
   - **Bug fix:** find the requirement the bug breaks. If no requirement covers the behaviour, the bug is a gap in the spec, so add one.
   - **Refactor with no behaviour change:** no spec edit, but it must still pass step 3.
   - Commit the spec change on its own, before the code: `spec: <summary>`.
2. **Code.** Implement only what the spec says. If the code needs behaviour the spec doesn't describe, go back to step 1.
3. **Confirm against the spec.** Before the code commit:
   - Run `pytest`.
   - For every requirement ID touched, verify it as its **Verified by** column says (unit test, or a manual or screenshot check, headless by default). Prefer adding a unit test where one is possible.
   - Re-read the changed code against the requirement text and look for behaviour the spec doesn't mention.
   - Update the row: set the status to `done` (or `partial` with the gap written in), and fill in **Verified by**. Update `roadmap.md` if a planned item landed.
4. **Commit** the code with a `Spec: ID, ID` trailer listing the requirements it implements or affects, and tell the user which IDs were verified and how.

When reporting to the user, say plainly if something could only be partly verified (e.g. the check needs Hyprland and the user had the app open, so the manual test was skipped).

## Commands

```bash
nix develop                    # devshell: python with pygobject and pytest, gtk4
pytest                         # unit tests (inside the devshell)
cd src && python -m wall_split # run (inside the devshell)
nix build                      # package -> ./result/bin/wall-split (also runs the tests)
nix flake check
```

The flake only sees git-tracked files. Run `git add` on new files before `nix build` or `nix develop`. `nix/package.nix` reads the name and version from `pyproject.toml`.

## Code layout

Keep this table current: one line per module, with the spec IDs it implements.

```
src/wall_split/app.py       Gtk.Application, the window, cut state and controls   WIN-1, WIN-2, WIN-6, WIN-7, WIN-8, WIN-9
src/wall_split/split.py     split math, no GTK                                    SPLIT-1, SPLIT-2
src/wall_split/pairings.py  common ratios, the pairing list, dropdown index, no GTK SPLIT-3, SPLIT-4, SPLIT-5, WIN-7
src/wall_split/dnd.py       drop target, async image load                          WIN-3, WIN-4, WIN-9
src/wall_split/preview.py   preview drawing area and cut line                     WIN-5
src/wall_split/export.py    save dialog, PNG writing, error alert                 EXP
src/wall_split/__main__.py  `python -m wall_split`                                INT-2
tests/                      pytest unit tests for the GTK-free modules
nix/package.nix             buildPythonApplication, wrapped by wrapGAppsHook4     INT-3
scripts/manual/             UI checks (lib.sh helpers; headless.sh runs one in a headless sway)
  smoke.sh                  window, app ID, opening files                         WIN-1, WIN-2, WIN-9
  preview.sh                preview fits the image, cut line placement           WIN-5
  slider.sh                 dropdown, slider and labels stay in sync              WIN-3, WIN-6, WIN-7, WIN-8, SPLIT-6
  rejected.sh               red border on a rejected file, state kept; content    WIN-3, WIN-4
  export.sh                 export through the save dialog, outputs vs source     EXP, PROD-4
spec/                       the specification
```

## Conventions

- Keep the dependency list short. Ask before adding a Python package or Nix input, and prefer GIO/GLib equivalents (`PROD-1`).
- No libadwaita. If a widget only exists in libadwaita, write the plain-GTK equivalent.
- Call `gi.require_version("Gtk", "4.0")` before importing from `gi.repository`.
- File I/O must not block the main loop (`PROD-4`): use the async GIO and GdkPixbuf APIs.
- Keep split math in GTK-free modules so it can be unit-tested.
- Look up PyGObject and GTK docs before guessing at APIs.
  - https://pygobject.gnome.org/
  - https://docs.gtk.org/gtk4/
- Comments only when the reason is not obvious (a GTK quirk, a rounding choice in the split math).
- Commits: `spec: <summary>` for spec changes, a `Spec: ID, ID` trailer on code commits, `BREAKING` in the body for incompatible changes. No Claude-Session links in commit messages.
- App-level Nix lives in this repo's `flake.nix`. Don't touch `~/Developer/nix-config` from here.

## Manual testing

Prefer adding a script to `scripts/manual/` (source `lib.sh`, which has the guards below built in) over ad-hoc commands. Each script names the spec IDs it checks. The scripts launch `./result/bin/wall-split`, so they need the package (`INT-3`) and a `nix build` first.

### Headless (default)

Run checks with `./scripts/manual/headless.sh ./scripts/manual/<name>.sh`. It starts a headless sway with its own D-Bus session and runtime dir, so it works while the screen is locked or the user has the app open, and never touches their windows. `lib.sh` switches to `swaymsg` when `HEADLESS` is set, so scripts don't change.

- The output defaults to 3840×2160 at scale 2. Set `HEADLESS_RES` and `HEADLESS_SCALE` to test other scales. Windows float, so they open at their default size.
- Send screenshots (`shot`, into `$OUT`) to the user when a change is visual.
- Headless sway drops the first key after `wtype` loads its keymap; `keys` sends a Shift tap first to absorb it.
- The headless runner can't drag a file into the window. Load images from the command line (`WIN-9`); only the drag itself needs a real Hyprland session.
- In headless mode `hyprctl` only answers `cursorpos` and `monitors`; anything else, and `ydotool`, fails instead of reaching the real session.

### On Hyprland

Run `./scripts/manual/<name>.sh` directly.

- Screenshots: `hyprctl clients -j` gives the window geometry, and `grim -g` captures it.
- Check `pidof hyprlock` first: if the screen is locked, grim captures the lock screen.
- New windows don't take focus. Run `hyprctl dispatch 'hl.dsp.focus({ window = "class:io.github.DisposableSoftware.WallSplit" })'`, then send keys with `wtype`. Always check `hyprctl activewindow` first, so keys never land in the user's other apps.
- The app is single-instance (`Gtk.Application`). If the user already has it open, a test launch only opens a window in *their* process. Check there are no `io.github.DisposableSoftware.WallSplit` clients before testing, and don't go ahead if there are. Find and kill test windows through `hyprctl clients -j` (`.pid`).
